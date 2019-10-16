#include <Python.h>

#define TINY 0.00001
#define MEMORY_INITIAL_SIZE 131072

#define DEBUG 0
#define PRUNING 1

#include <utils.cpp>
#include <solver.cpp>
#include <sub_interface.cpp>


PyObject* python_error(const char *ss) {
	PyErr_SetString(PyExc_TypeError, ss);
	return NULL;
}

static PyObject* setup_solver(PyObject* self, PyObject* args) {
	PyObject *ge_array, *le_array, *eq_array, *input_head;

	if (!PyArg_ParseTuple(args, "OOOO", &le_array, &eq_array, &ge_array, &input_head)) {
		return python_error("Argument must be two 2D python arrays, and a python array");
	}

	#if DEBUG==1
		printf("SETTING UP SOLVER\n");
		printf("FREEING ANY PREVIOUS MEMORY\n");
	#endif
	free_memory();
	
	int artificial_variables = 0;
	int* slackness_columns;
	// analyze tables and parse them into a single table with slack,excess and artificial variables.
	t = analyse_pyobject_tables(
		le_array,
		eq_array,
		ge_array,
		&artificial_variables,
		&slackness_columns,
		&players);
	if (t==NULL)
		return NULL;

	#if DEBUG==1
		printf("Analysed table:\n\tw=%i\th=%i\tAV=%i\n",t->w,t->h,artificial_variables);
		printf("\nTable Loaded:\n");
		t->print();
		printf("Slackness Columns:\n");
		for (int j=0; j<t->h; j++) printf("row %i, column %i\n",j,slackness_columns[j]);
	#endif
	
	// do simplex on artificial variables to determine initial feasible solution
	#if DEBUG==1
		printf("\nConducting Artificial variable simplex to get initial feasible solution:\n");
	#endif
	if (artificial_variables_simplex(t,artificial_variables) == false)
		return NULL;
	#if DEBUG==1
		printf("Artificial variable simplex resulting in table:\n");
		t->print();
		t->print_pivot_info();
	#endif

	// prune redundant columns/rows from the table representing redundant constraints
	#if PRUNING==1
		#if DEBUG==1
			printf("\nConducting Equation Pruning of redundant columns/rows from the table:\n");
			equation_pruning(t, slackness_columns);
			printf("Equation Pruning resulting in table:\n");
			t->print();
			printf("\n");
		#else
			equation_pruning(t, slackness_columns);
		#endif
	#endif
	free(slackness_columns);
	
	#if DEBUG==1
		printf("Loading Solver Working Memory\n");
	#endif
	setup_memory(t);

	#if DEBUG==1
		printf("SETTING UP HEAD\n");
	#endif
	if (set_head(input_head, t->w)==-1)
		return python_error("bad head.");
	#if DEBUG==1
		printf("Head set to:\n");
		printhead(master_head,t->w);
	#endif

	#if DEBUG==1
		printf("Setup Solver routine complete\n\n");
	#endif

	return PyFloat_FromDouble(1);
}


static PyObject* solve(PyObject* self, PyObject* args) {
	Mask player_mask, auxiliary_mask, coalition, anticoalition;
	player_mask.set_ones(players);
	auxiliary_mask.set_ones(t->w);
	auxiliary_mask.set(auxiliary_mask^player_mask);
	coalition.set_zero();
	anticoalition.set_zero();
	#if DEBUG==1
		printf("SOLVING\n");
	#endif
	PyObject *obj;

	#if DEBUG==1
		printf("parsing coalition\n");
	#endif
	Py_ssize_t TupleSize = PyTuple_Size(args);
	if(TupleSize != 1)
		return python_error("You must supply one argument.");
	obj = PyTuple_GetItem(args,0);
	if (PyNumber_Check(obj) != 1)
		return python_error("Non-numeric argument.");
	coalition.A = PyLong_AsUnsignedLong(PyNumber_Long(obj));
	if (PyErr_Occurred()!= NULL)
		return python_error("Non-numeric argument...");
	if (((~player_mask)&coalition).non_zero())
		return python_error("coalition too big!");
	anticoalition.set(player_mask^coalition);
	//int coalition_bits = coalition.count_bits();
	//int anticoalition_bits = anticoalition.count_bits();
	
	#if DEBUG==1
		printf("coalition: \t");
		coalition.print();
		printf("anticoalition: \t");
		anticoalition.print();
		printf("player_mask: \t");
		player_mask.print();
		printf("auxiliary_mask: \t");
		auxiliary_mask.print();
	#endif

	#if DEBUG==1
		printf("applying coalition\n");
	#endif

	double r = 0;
	for (int i=0; i< t->w; i++)
		temporary_head[i] = -(2*((int)(coalition.get_bit(i)))-1)*master_head[i];
	#if DEBUG==1
		printf("about to compute on coalition\n");
	#endif
	//r += 0.5*walk_back(prev_min_table, &coalition, temporary_head, true);
	r += 0.5*bilevel_solve(prev_min_table, &coalition, temporary_head, true);
	//r += 0.5*alt_bilevel_solve(prev_min_table, &coalition, temporary_head, true);
	for (int i=0; i< t->w; i++)
		temporary_head[i] = -(2*((int)(coalition.get_bit(i)))-1)*master_head[i];
	#if DEBUG==1
		printf("about to compute on anticoalition\n");
	#endif
	//r += 0.5*walk_back(prev_max_table, &anticoalition, temporary_head, false);
	r += 0.5*bilevel_solve(prev_max_table, &anticoalition, temporary_head, false);
	//r += 0.5*alt_bilevel_solve(prev_max_table, &anticoalition, temporary_head, false);
	
	return PyFloat_FromDouble(r);
}

static PyObject* spruik(PyObject* self, PyObject* args) {
	prev_max_table->load(t);
	prev_min_table->load(t);
	return PyFloat_FromDouble(1);
}
static PyObject* destroy(PyObject* self, PyObject* args) {
	free_memory();
	return PyFloat_FromDouble(1);
}

static PyObject* all_pivots(PyObject* self, PyObject* args) {
	PyObject *array;

	if (!PyArg_ParseTuple(args, "O", &array)) {
		return python_error("Argument must be single 2D python array");
	}
	
	Table* t;
	t = analyse_pyobject_table(array);
	t->reverse_engineer_pivots();
	t->calculate_pivots(true);

	/*printf("ALL_PIVOTS\n");
	t->print();
	t->print_pivot_info();
	t->print_pivotable_info();*/
	
	Mask_Memory* masks = (Mask_Memory*)malloc(sizeof(Mask_Memory));
	masks->setup(MEMORY_INITIAL_SIZE);
	Table_Memory* table_refs = (Table_Memory*)malloc(sizeof(Table_Memory));
	table_refs->setup(MEMORY_INITIAL_SIZE);
	Mask* new_mask = (Mask*)malloc(sizeof(Mask));
	
	masks->add(t->table_pivot_column_mask, false);
	table_refs->add(t);
	while(table_refs->length != 0) {
		t = table_refs->memory[table_refs->length-1];
		table_refs->length -= 1;
		/*printf("switch to: ");
		t->table_pivot_column_mask->print();
		printf("\n");*/
		for (int i=0; i<t->pivotable_number; i++) {
			new_mask->set(t->table_pivot_column_mask);
			new_mask->flip_bit(t->pivotable_columns[i]);
			if (t->pivotable_rows[i] != -1)
				new_mask->flip_bit(t->table_pivot_columns[t->pivotable_rows[i]]);
			if (masks->search(new_mask)==false) {
				/*printf("adding :");
				t->table_pivot_column_mask->print();
				printf(" to ");
				new_mask->print();
				printf("\n");*/
				masks->add(new_mask, false);
				Table* tt = (Table*)malloc(sizeof(Table));
				tt->initialise(t->w,t->h);
				tt->pivot(t,i);
				tt->calculate_pivots(true);
				table_refs->add(tt);
			}
		}
		for (int i=0; i<t->w; i++) {
			if (t->table_pivot_column_mask->get_bit(i)==1) {
				for (int j=0; j<t->h; j++)
					if (t->table_pivot_columns[j]==i) {
						if (t->get(t->w-1,j) == 0) {
							printf("XM\t");
						} else {
							printf("%i\t",(int)(t->get(t->w-1,j)));
						}
						break;
					}
			} else {
				printf("X\t");
			}
		}
		printf("\n");
		t->free_data();
		free(t);
	}
	
	free(new_mask);
	masks->clear();
	masks->destroy();
	free(masks);
	table_refs->free_all();
	table_refs->destroy();
	free(table_refs);
	return PyFloat_FromDouble(1);
}



static PyObject* all_pivots_dot(PyObject* self, PyObject* args) {
	free_memory();
	bool maximising;

	PyObject *array;
	PyObject *input_head;
	PyObject *number;
	PyObject *maximiser_number;
	Mask coalition;
	coalition.set_zero();
	
	Py_ssize_t TupleSize = PyTuple_Size(args);
	if(TupleSize != 4)
		return python_error("You must supply one argument.");
	array = PyTuple_GetItem(args,0);
	input_head = PyTuple_GetItem(args,1);
	number = PyTuple_GetItem(args,2);
	maximiser_number = PyTuple_GetItem(args,3);
	if (PyNumber_Check(number) != 1)
		return python_error("Non-numeric argument.");
	if (PyNumber_Check(maximiser_number) != 1)
		return python_error("Non-numeric argument.");
	coalition.A = PyLong_AsUnsignedLong(PyNumber_Long(number));
	if (PyInt_AsLong(maximiser_number) == 1.0) {
		maximising=true;
	} else {
		maximising=false;
	}
	if (PyErr_Occurred()!= NULL)
		return python_error("Error occured..");
	
	Table* t;
	t = analyse_pyobject_table(array);
	t->reverse_engineer_pivots();
	t->attempt_make_rational();
	t->calculate_pivots(false);
	
	
	setup_memory(t);
	if (set_head(input_head, t->w)==-1)
		return python_error("bad head.");

	for (int i=0; i< t->w; i++)
		master_head[i] = -(2*((int)(coalition.get_bit(i)))-1)*master_head[i];

	Mask_Memory* masks = (Mask_Memory*)malloc(sizeof(Mask_Memory));
	masks->setup(MEMORY_INITIAL_SIZE);
	Table_Memory* table_refs = (Table_Memory*)malloc(sizeof(Table_Memory));
	table_refs->setup(MEMORY_INITIAL_SIZE);
	Mask* new_mask = (Mask*)malloc(sizeof(Mask));
	
	masks->add(t->table_pivot_column_mask, false);
	table_refs->add(t);

	//coalition.print();

	printf("graph graphname {\n\t");
	t->table_pivot_column_mask->print_small();
	printf(" [");
	t->apply_to_head(master_head,temporary_head);
	printf("label=\"");
	t->table_pivot_column_mask->print_small();
	printf(",%.1f\",",temporary_head[t->w-1]);
	if (t->check_subset_improvable(&coalition, temporary_head, !maximising))
		printf("color=blue");
	printf("];\n");

	while(table_refs->length != 0) {
		t = table_refs->memory[table_refs->length-1];
		table_refs->length -= 1;
		/*printf("switch to: ");
		t->table_pivot_column_mask->print();
		printf("\n");*/
		for (int i=0; i<t->pivotable_number; i++) {
			new_mask->set(t->table_pivot_column_mask);
			new_mask->flip_bit(t->pivotable_columns[i]);
			if (t->pivotable_rows[i] != -1)
				new_mask->flip_bit(t->table_pivot_columns[t->pivotable_rows[i]]);
			if (masks->search(new_mask)==false) {
				masks->add(new_mask, false);
				Table* tt = (Table*)malloc(sizeof(Table));
				tt->initialise(t->w,t->h);
				tt->pivot(t,i);
				tt->calculate_pivots(false);
				table_refs->add(tt);
				
				printf("\t");
				tt->table_pivot_column_mask->print_small();
				printf(" [");
				tt->apply_to_head(master_head,temporary_head);
				printf("label=\"");
				tt->table_pivot_column_mask->print_small();
				printf(",%.1f\",",temporary_head[tt->w-1]);
				if (tt->check_subset_improvable(&coalition, temporary_head, !maximising))
					printf("color=blue");
				printf("];\n");
			}
			if (t->table_pivot_column_mask->A > new_mask->A) {
				printf("\t");
				t->table_pivot_column_mask->print_small();
				printf(" -- ");
				new_mask->print_small();
				printf(";\n");
			}
		}
		t->free_data();
		free(t);
	}
	printf("}\n");
	
	free(new_mask);
	masks->clear();
	masks->destroy();
	free(masks);
	table_refs->free_all();
	table_refs->destroy();
	free(table_refs);
	return PyFloat_FromDouble(1);
}




static char setup_solver_docs[] = "setup_solver(): does all the setup for the solver apparatus, conducting Phase I feasibility solving and initialising all memory.\n";
static char solve_docs[] = "solve(): for a coalition calculate the minimax value.\n";
static char spruik_docs[] = "asdfas.\n";
static char destroy_docs[] = "frees all memory.\n";

static PyMethodDef bilevel_solver_funcs[] = {
	{"setup_solver", (PyCFunction)setup_solver, 
		METH_VARARGS, setup_solver_docs},
	{"solve", (PyCFunction)solve, 
		METH_VARARGS, solve_docs},
	{"spruik", (PyCFunction)spruik, 
		METH_NOARGS, spruik_docs},
	{"destroy", (PyCFunction)destroy, 
		METH_NOARGS, destroy_docs},
	{"all_pivots", (PyCFunction)all_pivots, 
		METH_VARARGS, setup_solver_docs},
	{"all_pivots_dot", (PyCFunction)all_pivots_dot, 
		METH_VARARGS, setup_solver_docs},
		{NULL}
};
extern "C" {
	void initbilevel_solver(void) {
		Py_InitModule("bilevel_solver", bilevel_solver_funcs);
	}
}
