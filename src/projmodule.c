/* projmodule.c
   Magnus Hagdorn, March 2002

   python module using libproj to do cartographic projections */

#include <Python.h>
#include <Numeric/arrayobject.h>
#include <projects.h>
#include <stdio.h>

static PyObject * proj_project(PyObject * self, PyObject * args, PyObject * keywds)
{
  PyArrayObject *geo_loc;
  PyArrayObject *locations;
  PyListObject  *proj_params;
  PyObject *o;

  int inv = 0;
  char **params;
  int num_loc, num_params;
  int dimensions[2];
  int i;

  /* projection stuff */
  PJ *ref;
  projUV data;

  static char *kwlist[] = {"params","loc","inv",NULL};

  /* parsing arguments */
  if (!PyArg_ParseTupleAndKeywords(args, keywds, "O!O!|i",kwlist, &PyList_Type, &proj_params,&PyArray_Type, &geo_loc, &inv))
    return NULL;
  /* checking dimensions and type of array */
  if (geo_loc->nd != 2 || geo_loc->descr->type_num != PyArray_FLOAT)
    {
      PyErr_SetString(PyExc_ValueError,"array must be 2D and of type float");
      return NULL;
    }
  
  /* creating output array */
  dimensions[0] = geo_loc->dimensions[0];
  dimensions[1] = geo_loc->dimensions[1];
  locations = (PyArrayObject *) PyArray_FromDims(2, dimensions, PyArray_FLOAT);


  /* getting number of locations */
  num_loc = geo_loc->dimensions[1];

  /* setting up projection */
  num_params = PyList_Size((PyObject *) proj_params);
  params = (char **) malloc(num_params*sizeof(char *));
  for (i=0;i<num_params;i++)
    {
      o = PyList_GetItem((PyObject *) proj_params, i);
      if (PyString_Check(o)) 
	*(params+i) = PyString_AsString(o);
      else
	{
	  PyErr_SetString(PyExc_ValueError,"Projection parameter list contains non-string types");
	  free(params);
	  return NULL;
	}
    }

  /* setup projection */
  if (! (ref=pj_init(num_params,params)))
    {
      PyErr_SetString(PyExc_RuntimeError,pj_strerrno(pj_errno));
      free(params);
      return NULL;
    }

  /* do the projection */
  if (inv==1)
    {
      /* inverse projection */
      for (i=0;i<num_loc;i++)
	{
	  data.u = *(float *) (geo_loc->data+i*geo_loc->strides[1]);
	  data.v = *(float *) (geo_loc->data+i*geo_loc->strides[1] + locations->strides[0]);
	  
	  data = pj_inv(data,ref);
	  
	  *(float *) (locations->data+i*locations->strides[1]) = (float) data.u * RAD_TO_DEG;
	  *(float *) (locations->data+i*locations->strides[1] + locations->strides[0]) = (float) data.v * RAD_TO_DEG;
	}
    }
  else
    {
      /* forward projection */
      for (i=0;i<num_loc;i++)
	{
	  data.u = *(float *) (geo_loc->data+i*geo_loc->strides[1]) * DEG_TO_RAD;
	  data.v = *(float *) (geo_loc->data+i*geo_loc->strides[1] + locations->strides[0]) * DEG_TO_RAD;
	  
	  data = pj_fwd(data,ref);
	  
	  *(float *) (locations->data+i*locations->strides[1]) = (float) data.u;
	  *(float *) (locations->data+i*locations->strides[1] + locations->strides[0]) = (float) data.v;
	}
    }
  

  /* the end */
  
  free(params);
  return PyArray_Return(locations);
}

static PyMethodDef ProjMethods[] = {
  {"project",  (PyCFunction)proj_project, METH_VARARGS|METH_KEYWORDS, "Do Projection..."},
        {NULL, NULL, 0, NULL}        /* Sentinel */
};


void initproj(void)
{
  Py_InitModule("proj", ProjMethods);
  import_array();
}

