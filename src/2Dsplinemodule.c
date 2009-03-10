/* 2Dsplinemodule.c
   Magnus Hagdorn, March 2002

   python module doing 2D spline interpolation using gsl splines */

#include <Python.h>
#include <numpy/arrayobject.h>
#include <gsl/gsl_errno.h>
#include <gsl/gsl_spline.h>
#include <stdio.h>

static PyObject * TwoDspline_1Dinterp(PyObject * self, PyObject * args)
{
  PyArrayObject *Py_x, *Py_y, *Py_loc;
  PyArrayObject *Py_interpolated;

  /* GSL spline definitions */
  gsl_spline *spline;
  gsl_interp_accel *accel;

  int num_loc;
  int i;
  double *x, *y, *loc, res;
  int status;

  /* parsing arguments */
  if (!PyArg_ParseTuple(args, "O!O!O!", &PyArray_Type, &Py_x, &PyArray_Type, &Py_y, &PyArray_Type, &Py_loc))
    return NULL;
  /* checking dimensions and type of arrays */
  if (Py_x->nd != 1 || Py_x->descr->type_num != NPY_FLOAT)
    {
      PyErr_SetString(PyExc_ValueError,"array x must be 1D and of type float");
      return NULL;
    }
  if (Py_y->nd != 1 || Py_y->descr->type_num != NPY_FLOAT)
    {
      PyErr_SetString(PyExc_ValueError,"array y must be 1D and of type float");
      return NULL;
    }
  if (Py_loc->nd != 1 || Py_loc->descr->type_num != NPY_FLOAT)
    {
      PyErr_SetString(PyExc_ValueError,"array locations must be 1D and of type float");
      return NULL;
    }
  /* checking array sizes */
  if (Py_x->dimensions[0] != Py_y->dimensions[0])
    {
      PyErr_SetString(PyExc_ValueError,"dimensions of x do not match y dimension");
      return NULL;
    }

  /* creating output array */
  num_loc = Py_loc->dimensions[0];
  Py_interpolated = (PyArrayObject *) PyArray_FromDims(1, &num_loc, NPY_FLOAT);

  /* extracting data */
  x = (double *) malloc(sizeof(double)*Py_x->dimensions[0]);
  for (i=0;i<Py_x->dimensions[0];i++)
    *(x+i) = *(float *) (Py_x->data+i*Py_x->strides[0]);

  y = (double *) malloc(sizeof(double)*Py_y->dimensions[0]);
  for (i=0;i<Py_y->dimensions[0];i++)
    *(y+i) = *(float *) (Py_y->data+i*Py_y->strides[0]);

  loc = (double *) malloc(sizeof(double)*num_loc);
  for (i=0;i<num_loc;i++)
    *(loc+i) = *(float *) (Py_loc->data+i*Py_loc->strides[0]);

  /* setting up splines */
  spline = gsl_spline_alloc(gsl_interp_cspline,Py_x->dimensions[0]);
  accel = gsl_interp_accel_alloc();

  /* evalutating splines */
  status = gsl_spline_init(spline, x, y, Py_x->dimensions[0]);
  if (status)
    {
      PyErr_SetString(PyExc_ValueError,gsl_strerror (status));
      return NULL;	
    }
  for (i=0;i<num_loc;i++)
    {
      status = gsl_spline_eval_e(spline,*(loc+i),accel, &res);
      if (status)
	{
	  PyErr_SetString(PyExc_ValueError,gsl_strerror (status));
	  return NULL;	
	}
      *(float *) (Py_interpolated->data+i*Py_interpolated->strides[0]) = res;      
    }

  /* cleaning up */
  free(x);
  free(y);
  free(loc);
  gsl_spline_free(spline);
  gsl_interp_accel_free(accel);

  return PyArray_Return(Py_interpolated); 
}

static PyObject * TwoDspline_1Dinterp_deriv(PyObject * self, PyObject * args)
{
  PyArrayObject *Py_x, *Py_y, *Py_loc;
  PyArrayObject *Py_interpolated;

  /* GSL spline definitions */
  gsl_spline *spline;
  gsl_interp_accel *accel;

  int num_loc;
  int i;
  double *x, *y, *loc, res;
  int status;

  /* parsing arguments */
  if (!PyArg_ParseTuple(args, "O!O!O!", &PyArray_Type, &Py_x, &PyArray_Type, &Py_y, &PyArray_Type, &Py_loc))
    return NULL;
  /* checking dimensions and type of arrays */
  if (Py_x->nd != 1 || Py_x->descr->type_num != NPY_FLOAT)
    {
      PyErr_SetString(PyExc_ValueError,"array x must be 1D and of type float");
      return NULL;
    }
  if (Py_y->nd != 1 || Py_y->descr->type_num != NPY_FLOAT)
    {
      PyErr_SetString(PyExc_ValueError,"array y must be 1D and of type float");
      return NULL;
    }
  if (Py_loc->nd != 1 || Py_loc->descr->type_num != NPY_FLOAT)
    {
      PyErr_SetString(PyExc_ValueError,"array locations must be 1D and of type float");
      return NULL;
    }
  /* checking array sizes */
  if (Py_x->dimensions[0] != Py_y->dimensions[0])
    {
      PyErr_SetString(PyExc_ValueError,"dimensions of x do not match y dimension");
      return NULL;
    }

  /* creating output array */
  num_loc = Py_loc->dimensions[0];
  Py_interpolated = (PyArrayObject *) PyArray_FromDims(1, &num_loc, NPY_FLOAT);

  /* extracting data */
  x = (double *) malloc(sizeof(double)*Py_x->dimensions[0]);
  for (i=0;i<Py_x->dimensions[0];i++)
    *(x+i) = *(float *) (Py_x->data+i*Py_x->strides[0]);

  y = (double *) malloc(sizeof(double)*Py_y->dimensions[0]);
  for (i=0;i<Py_y->dimensions[0];i++)
    *(y+i) = *(float *) (Py_y->data+i*Py_y->strides[0]);

  loc = (double *) malloc(sizeof(double)*num_loc);
  for (i=0;i<num_loc;i++)
    *(loc+i) = *(float *) (Py_loc->data+i*Py_loc->strides[0]);

  /* setting up splines */
  spline = gsl_spline_alloc(gsl_interp_cspline,Py_x->dimensions[0]);
  accel = gsl_interp_accel_alloc();

  /* evalutating splines */
  status = gsl_spline_init(spline, x, y, Py_x->dimensions[0]);
  if (status)
    {
      PyErr_SetString(PyExc_ValueError,gsl_strerror (status));
      return NULL;	
    }
  for (i=0;i<num_loc;i++)
    {
      status = gsl_spline_eval_deriv_e(spline,*(loc+i),accel, &res);
      if (status)
	{
	  PyErr_SetString(PyExc_ValueError,gsl_strerror (status));
	  return NULL;	
	}
      *(float *) (Py_interpolated->data+i*Py_interpolated->strides[0]) = res;      
    }

  /* cleaning up */
  free(x);
  free(y);
  free(loc);
  gsl_spline_free(spline);
  gsl_interp_accel_free(accel);

  return PyArray_Return(Py_interpolated); 
}


static PyObject * TwoDspline_2Dinterp(PyObject * self, PyObject * args)
{
  PyArrayObject *Py_x, *Py_y, *Py_z, *Py_locations;
  PyArrayObject *Py_interpolated;

  /* GSL spline definitions */
  gsl_spline *y_spline;
  gsl_spline **x_splines;
  gsl_interp_accel *y_accel;
  gsl_interp_accel **x_accels;
  
  int num_loc;
  int i,j;
  double *x, *y, **z, *zy;
  double loc_x, loc_y, res;
  int status;
  
  /* parsing arguments */
  if (!PyArg_ParseTuple(args, "O!O!O!O!", &PyArray_Type, &Py_x, &PyArray_Type, &Py_y, &PyArray_Type, &Py_z, &PyArray_Type, &Py_locations))
    return NULL;
  /* checking dimensions and type of arrays */
  if (Py_x->nd != 1 || Py_x->descr->type_num != NPY_FLOAT)
    {
      PyErr_SetString(PyExc_ValueError,"array x must be 1D and of type float");
      return NULL;
    }
  if (Py_y->nd != 1 || Py_y->descr->type_num != NPY_FLOAT)
    {
      PyErr_SetString(PyExc_ValueError,"array y must be 1D and of type float");
      return NULL;
    }
  if (Py_z->nd != 2 || Py_z->descr->type_num != NPY_FLOAT)
    {
      PyErr_SetString(PyExc_ValueError,"array z must be 2D and of type float");
      return NULL;
    }
  if (Py_locations->nd != 2 || Py_locations->descr->type_num != NPY_FLOAT)
    {
      PyErr_SetString(PyExc_ValueError,"array locations must be 2D and of type float");
      return NULL;
    }
  
  /* checking array sizes */
  if (Py_x->dimensions[0] != Py_z->dimensions[0] || Py_y->dimensions[0] != Py_z->dimensions[1])
    {
      PyErr_SetString(PyExc_ValueError,"dimensions of z do not match x,y dimensions");
      return NULL;
    }

  /* creating output array */
  num_loc = Py_locations->dimensions[1];
  Py_interpolated = (PyArrayObject *) PyArray_FromDims(1, &num_loc, NPY_FLOAT);

  /* extracting data */
  x = (double *) malloc(sizeof(double)*Py_x->dimensions[0]);
  for (i=0;i<Py_x->dimensions[0];i++)
    *(x+i) = *(float *) (Py_x->data+i*Py_x->strides[0]);

  y = (double *) malloc(sizeof(double)*Py_y->dimensions[0]);
  for (i=0;i<Py_y->dimensions[0];i++)
    *(y+i) = *(float *) (Py_y->data+i*Py_y->strides[0]);

  z = (double **) malloc(sizeof(double*)*Py_y->dimensions[0]);
  for (j=0;j<Py_y->dimensions[0];j++)
    {
      *(z+j) = (double *) malloc(sizeof(double)*Py_x->dimensions[0]);
      for (i=0;i<Py_x->dimensions[0];i++)
	*(*(z+j)+i) = *(float *) (Py_z->data +i*Py_z->strides[0] + j*Py_z->strides[1]);
    }

  /* setting up splines */
  x_splines = (gsl_spline **) malloc(sizeof(gsl_spline *)*Py_y->dimensions[0]);
  x_accels = (gsl_interp_accel **) malloc(sizeof(gsl_interp_accel *)*Py_y->dimensions[0]);
  for (j=0;j<Py_y->dimensions[0];j++)
    {
      *(x_splines+j) = gsl_spline_alloc(gsl_interp_cspline,Py_x->dimensions[0]);
      status = gsl_spline_init(*(x_splines+j), x, *(z+j), Py_x->dimensions[0]);
      if (status)
	{
	  PyErr_SetString(PyExc_ValueError,gsl_strerror (status));
	  return NULL;	
	}
      *(x_accels+j) = gsl_interp_accel_alloc();
    }
  y_spline = gsl_spline_alloc(gsl_interp_cspline,Py_y->dimensions[0]);
  y_accel = gsl_interp_accel_alloc();

  /* evalutating splines */
  zy = (double *) malloc(sizeof(double)*Py_y->dimensions[0]);
  for (i=0;i<num_loc;i++)  /* loop over locations */
    {
      loc_x = *(float *) (Py_locations->data+i*Py_locations->strides[1]);
      loc_y = *(float *) (Py_locations->data+i*Py_locations->strides[1]+Py_locations->strides[0]);
      for (j=0;j<Py_y->dimensions[0];j++)  /* loop over rows and proccess them */
	{
	  status = gsl_spline_eval_e(*(x_splines+j),loc_x,*(x_accels+j),zy+j);
	  if (status)
	    {
	      PyErr_SetString(PyExc_ValueError,gsl_strerror (status));
	      return NULL;	
	    }
	}
      status = gsl_spline_init(y_spline, y, zy, Py_y->dimensions[0]);
      if (status)
	{
	  PyErr_SetString(PyExc_ValueError,gsl_strerror (status));
	  return NULL;	
	}
      status = gsl_spline_eval_e(y_spline,loc_y,y_accel, &res);
      if (status)
	{
	  PyErr_SetString(PyExc_ValueError,gsl_strerror (status));
	  return NULL;	
	}
      *(float *) (Py_interpolated->data+i*Py_interpolated->strides[0]) = res;
    }

  /* cleaning up */
  free(x);
  free(y);
  free(zy);
  gsl_spline_free(y_spline);
  gsl_interp_accel_free(y_accel);
  for (j=0;j<Py_y->dimensions[0];j++)
    {
      free(*(z+j));
      gsl_spline_free(*(x_splines+j));
      gsl_interp_accel_free(*(x_accels+j));
    }
  free(x_splines);
  free(x_accels);

  return PyArray_Return(Py_interpolated); 
}

static PyMethodDef TwoDsplineMethods[] = {
  {"TwoDspline",  TwoDspline_2Dinterp, METH_VARARGS, "Do 2Dsplines..."},
  {"OneDspline_d", TwoDspline_1Dinterp_deriv, METH_VARARGS, "Do derivative of 1Dsplines..."},
  {"OneDspline",  TwoDspline_1Dinterp, METH_VARARGS, "Do 1Dsplines..."},
        {NULL, NULL, 0, NULL}        /* Sentinel */
};


void initTwoDspline(void)
{
  Py_InitModule("TwoDspline", TwoDsplineMethods);
  import_array();
}
