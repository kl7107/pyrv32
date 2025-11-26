/*
 ****************************************************************************
 *
 *                   "DHRYSTONE" Benchmark Program
 *                   -----------------------------
 *                                                                            
 *  Version:    C, Version 2.1
 *                                                                            
 *  File:       dhry_1.c (part 2 of 3)
 *
 *  Date:       May 25, 1988
 *
 *  Author:     Reinhold P. Weicker
 *
 ****************************************************************************/

#include "dhry.h"
#include "string.h"
#include "stdlib.h"

/* Global Variables: */

Rec_Pointer     Ptr_Glob,
                Next_Ptr_Glob;
int             Int_Glob;
Boolean         Bool_Glob;
char            Ch_1_Glob,
                Ch_2_Glob;
int             Arr_1_Glob [50];
int             Arr_2_Glob [50] [50];

extern void *malloc();

/* Forward declarations */
void Proc_1();
void Proc_2();
void Proc_3();
void Proc_4();
void Proc_5();
void Proc_6();
void Proc_7();
void Proc_8();
Boolean Func_2();
Boolean Func_3();

Enumeration Func_1();
        /* forward declaration necessary since Enumeration may not simply be int */

#ifndef REG
        Boolean Reg = false;
#define REG
        /* REG becomes defined as empty */
        /* i.e. no register variables   */
#else
        Boolean Reg = true;
#endif

/* variables for time measurement: */

#define Too_Small_Time 2
                /* Measurements should last at least 2 seconds */

long            Begin_Time,
                End_Time,
                User_Time;

long            Microseconds,
                Dhrystones_Per_Second;

/* end of variables for time measurement */

/* Simple printf-like function for UART output */
void uart_print(const char *s) {
    while (*s) {
        *(volatile char *)0x10000000 = *s++;
    }
}

void uart_print_int(int val) {
    char buf[12];
    int i = 0;
    int is_neg = 0;
    
    if (val < 0) {
        is_neg = 1;
        val = -val;
    }
    
    if (val == 0) {
        buf[i++] = '0';
    } else {
        while (val > 0) {
            buf[i++] = '0' + (val % 10);
            val /= 10;
        }
    }
    
    if (is_neg) {
        buf[i++] = '-';
    }
    
    /* Reverse */
    for (int j = 0; j < i / 2; j++) {
        char tmp = buf[j];
        buf[j] = buf[i - 1 - j];
        buf[i - 1 - j] = tmp;
    }
    buf[i] = '\0';
    
    uart_print(buf);
}

/* Simplified time measurement - just count instructions executed */
volatile unsigned int *mtime_ms = (volatile unsigned int *)0x10000004;

long clock_ms(void) {
    /* Read millisecond timer */
    return (long)*mtime_ms;
}

void main ()
/*****/

  /* main program, corresponds to procedures        */
  /* Main and Proc_0 in the Ada version             */
{
        One_Fifty       Int_1_Loc;
  REG   One_Fifty       Int_2_Loc;
        One_Fifty       Int_3_Loc;
  REG   char            Ch_Index;
        Enumeration     Enum_Loc;
        Str_30          Str_1_Loc;
        Str_30          Str_2_Loc;
  REG   int             Run_Index;
  REG   int             Number_Of_Runs;

  /* Initializations */

  Next_Ptr_Glob = (Rec_Pointer) malloc (sizeof (Rec_Type));
  Ptr_Glob = (Rec_Pointer) malloc (sizeof (Rec_Type));

  Ptr_Glob->Ptr_Comp                    = Next_Ptr_Glob;
  Ptr_Glob->Discr                       = Ident_1;
  Ptr_Glob->variant.var_1.Enum_Comp     = Ident_3;
  Ptr_Glob->variant.var_1.Int_Comp      = 40;
  strcpy (Ptr_Glob->variant.var_1.Str_Comp, 
          "DHRYSTONE PROGRAM, SOME STRING");
  strcpy (Str_1_Loc, "DHRYSTONE PROGRAM, 1'ST STRING");

  Arr_2_Glob [8][7] = 10;
        /* Was missing in published program. Without this statement,    */
        /* Arr_2_Glob [8][7] would have an undefined value.             */
        /* Warning: With 16-Bit processors and Number_Of_Runs > 32000,  */
        /* overflow may occur for this array element.                   */

  uart_print("\n");
  uart_print("Dhrystone Benchmark, Version 2.1 (Language: C)\n");
  uart_print("\n");

  Number_Of_Runs = 10000;
  uart_print("Execution starts, ");
  uart_print_int(Number_Of_Runs);
  uart_print(" runs through Dhrystone\n");

  /***************/
  /* Start timer */
  /***************/
 
  Begin_Time = clock_ms();

  for (Run_Index = 1; Run_Index <= Number_Of_Runs; ++Run_Index)
  {

    Proc_5();
    Proc_4();
      /* Ch_1_Glob == 'A', Ch_2_Glob == 'B', Bool_Glob == true */
    Int_1_Loc = 2;
    Int_2_Loc = 3;
    strcpy (Str_2_Loc, "DHRYSTONE PROGRAM, 2'ND STRING");
    Enum_Loc = Ident_2;
    Bool_Glob = ! Func_2 (Str_1_Loc, Str_2_Loc);
      /* Bool_Glob == 1 */
    while (Int_1_Loc < Int_2_Loc)  /* loop body executed once */
    {
      Int_3_Loc = 5 * Int_1_Loc - Int_2_Loc;
        /* Int_3_Loc == 7 */
      Proc_7 (Int_1_Loc, Int_2_Loc, &Int_3_Loc);
        /* Int_3_Loc == 7 */
      Int_1_Loc += 1;
    } /* while */
      /* Int_1_Loc == 3, Int_2_Loc == 3, Int_3_Loc == 7 */
    Proc_8 (Arr_1_Glob, Arr_2_Glob, Int_1_Loc, Int_3_Loc);
      /* Int_Glob == 5 */
    Proc_1 (Ptr_Glob);
    for (Ch_Index = 'A'; Ch_Index <= Ch_2_Glob; ++Ch_Index)
                             /* loop body executed twice */
    {
      if (Enum_Loc == Func_1 (Ch_Index, 'C'))
          /* then, not executed */
        {
        Proc_6 (Ident_1, &Enum_Loc);
        strcpy (Str_2_Loc, "DHRYSTONE PROGRAM, 3'RD STRING");
        Int_2_Loc = Run_Index;
        Int_Glob = Run_Index;
        }
    }
      /* Int_1_Loc == 3, Int_2_Loc == 3, Int_3_Loc == 7 */
    Int_2_Loc = Int_2_Loc * Int_1_Loc;
    Int_1_Loc = Int_2_Loc / Int_3_Loc;
    Int_2_Loc = 7 * (Int_2_Loc - Int_3_Loc) - Int_1_Loc;
      /* Int_1_Loc == 1, Int_2_Loc == 13, Int_3_Loc == 7 */
    Proc_2 (&Int_1_Loc);
      /* Int_1_Loc == 5 */

  } /* loop "for Run_Index" */

  /**************/
  /* Stop timer */
  /**************/
  
  End_Time = clock_ms();

  uart_print("Execution ends\n");
  uart_print("\n");
  uart_print("Final values of the variables used in the benchmark:\n");
  uart_print("\n");
  uart_print("Int_Glob:            ");
  uart_print_int(Int_Glob);
  uart_print("\n");
  uart_print("        should be:   5\n");
  uart_print("Bool_Glob:           ");
  uart_print_int(Bool_Glob);
  uart_print("\n");
  uart_print("        should be:   1\n");
  uart_print("Ch_1_Glob:           ");
  *(volatile char *)0x10000000 = Ch_1_Glob;
  uart_print("\n");
  uart_print("        should be:   A\n");
  uart_print("Ch_2_Glob:           ");
  *(volatile char *)0x10000000 = Ch_2_Glob;
  uart_print("\n");
  uart_print("        should be:   B\n");
  uart_print("Arr_1_Glob[8]:       ");
  uart_print_int(Arr_1_Glob[8]);
  uart_print("\n");
  uart_print("        should be:   7\n");
  uart_print("Arr_2_Glob[8][7]:    ");
  uart_print_int(Arr_2_Glob[8][7]);
  uart_print("\n");
  uart_print("        should be:   Number_Of_Runs + 10\n");
  uart_print("Ptr_Glob->\n");
  uart_print("  Ptr_Comp:          ");
  uart_print_int((int)Ptr_Glob->Ptr_Comp);
  uart_print("\n");
  uart_print("        should be:   (implementation-dependent)\n");
  uart_print("  Discr:             ");
  uart_print_int(Ptr_Glob->Discr);
  uart_print("\n");
  uart_print("        should be:   0\n");
  uart_print("  Enum_Comp:         ");
  uart_print_int(Ptr_Glob->variant.var_1.Enum_Comp);
  uart_print("\n");
  uart_print("        should be:   2\n");
  uart_print("  Int_Comp:          ");
  uart_print_int(Ptr_Glob->variant.var_1.Int_Comp);
  uart_print("\n");
  uart_print("        should be:   17\n");
  uart_print("  Str_Comp:          ");
  uart_print(Ptr_Glob->variant.var_1.Str_Comp);
  uart_print("\n");
  uart_print("        should be:   DHRYSTONE PROGRAM, SOME STRING\n");
  uart_print("Next_Ptr_Glob->\n");
  uart_print("  Ptr_Comp:          ");
  uart_print_int((int)Next_Ptr_Glob->Ptr_Comp);
  uart_print("\n");
  uart_print("        should be:   (implementation-dependent), same as above\n");
  uart_print("  Discr:             ");
  uart_print_int(Next_Ptr_Glob->Discr);
  uart_print("\n");
  uart_print("        should be:   0\n");
  uart_print("  Enum_Comp:         ");
  uart_print_int(Next_Ptr_Glob->variant.var_1.Enum_Comp);
  uart_print("\n");
  uart_print("        should be:   1\n");
  uart_print("  Int_Comp:          ");
  uart_print_int(Next_Ptr_Glob->variant.var_1.Int_Comp);
  uart_print("\n");
  uart_print("        should be:   18\n");
  uart_print("  Str_Comp:          ");
  uart_print(Next_Ptr_Glob->variant.var_1.Str_Comp);
  uart_print("\n");
  uart_print("        should be:   DHRYSTONE PROGRAM, SOME STRING\n");
  uart_print("Int_1_Loc:           ");
  uart_print_int(Int_1_Loc);
  uart_print("\n");
  uart_print("        should be:   5\n");
  uart_print("Int_2_Loc:           ");
  uart_print_int(Int_2_Loc);
  uart_print("\n");
  uart_print("        should be:   13\n");
  uart_print("Int_3_Loc:           ");
  uart_print_int(Int_3_Loc);
  uart_print("\n");
  uart_print("        should be:   7\n");
  uart_print("Enum_Loc:            ");
  uart_print_int(Enum_Loc);
  uart_print("\n");
  uart_print("        should be:   1\n");
  uart_print("Str_1_Loc:           ");
  uart_print(Str_1_Loc);
  uart_print("\n");
  uart_print("        should be:   DHRYSTONE PROGRAM, 1'ST STRING\n");
  uart_print("Str_2_Loc:           ");
  uart_print(Str_2_Loc);
  uart_print("\n");
  uart_print("        should be:   DHRYSTONE PROGRAM, 2'ND STRING\n");
  uart_print("\n");

  User_Time = End_Time - Begin_Time;

  uart_print("Microseconds for one run through Dhrystone: ");
  uart_print_int((User_Time * 1000) / Number_Of_Runs);
  uart_print("\n");
  uart_print("Dhrystones per Second:                      ");
  if (User_Time > 0) {
    Dhrystones_Per_Second = (Number_Of_Runs * 1000) / User_Time;
    uart_print_int(Dhrystones_Per_Second);
  } else {
    uart_print("(too fast to measure)");
  }
  uart_print("\n");
  uart_print("\n");

  uart_print("Benchmark completed\n");

  /* Halt */
  while(1);
}


void Proc_1 (Ptr_Val_Par)
/******************/

REG Rec_Pointer Ptr_Val_Par;
    /* executed once */
{
  REG Rec_Pointer Next_Record = Ptr_Val_Par->Ptr_Comp;  
                                        /* == Ptr_Glob_Next */
  /* Local variable, initialized with Ptr_Val_Par->Ptr_Comp,    */
  /* corresponds to "rename" in Ada, "with" in Pascal           */
  
  structassign (*Ptr_Val_Par->Ptr_Comp, *Ptr_Glob); 
  Ptr_Val_Par->variant.var_1.Int_Comp = 5;
  Next_Record->variant.var_1.Int_Comp 
        = Ptr_Val_Par->variant.var_1.Int_Comp;
  Next_Record->Ptr_Comp = Ptr_Val_Par->Ptr_Comp;
  Proc_3 (&Next_Record->Ptr_Comp);
    /* Ptr_Val_Par->Ptr_Comp->Ptr_Comp 
                        == Ptr_Glob->Ptr_Comp */
  if (Next_Record->Discr == Ident_1)
    /* then, executed */
  {
    Next_Record->variant.var_1.Int_Comp = 6;
    Proc_6 (Ptr_Val_Par->variant.var_1.Enum_Comp, 
           &Next_Record->variant.var_1.Enum_Comp);
    Next_Record->Ptr_Comp = Ptr_Glob->Ptr_Comp;
    Proc_7 (Next_Record->variant.var_1.Int_Comp, 10, 
           &Next_Record->variant.var_1.Int_Comp);
  }
  else /* not executed */
    structassign (*Ptr_Val_Par, *Ptr_Val_Par->Ptr_Comp);
} /* Proc_1 */


void Proc_2 (Int_Par_Ref)
/******************/
    /* executed once */
    /* *Int_Par_Ref == 1, becomes 4 */

One_Fifty   *Int_Par_Ref;
{
  One_Fifty  Int_Loc;  
  Enumeration   Enum_Loc;

  Int_Loc = *Int_Par_Ref + 10;
  do /* executed once */
    if (Ch_1_Glob == 'A')
      /* then, executed */
    {
      Int_Loc -= 1;
      *Int_Par_Ref = Int_Loc - Int_Glob;
      Enum_Loc = Ident_1;
    } /* if */
  while (Enum_Loc != Ident_1); /* true */
} /* Proc_2 */


void Proc_3 (Ptr_Ref_Par)
/******************/
    /* executed once */
    /* Ptr_Ref_Par becomes Ptr_Glob */

Rec_Pointer *Ptr_Ref_Par;

{
  if (Ptr_Glob != Null)
    /* then, executed */
    *Ptr_Ref_Par = Ptr_Glob->Ptr_Comp;
  Proc_7 (10, Int_Glob, &Ptr_Glob->variant.var_1.Int_Comp);
} /* Proc_3 */


void Proc_4 () /* without parameters */
/*******/
    /* executed once */
{
  Boolean Bool_Loc;

  Bool_Loc = Ch_1_Glob == 'A';
  Bool_Glob = Bool_Loc | Bool_Glob;
  Ch_2_Glob = 'B';
} /* Proc_4 */


void Proc_5 () /* without parameters */
/*******/
    /* executed once */
{
  Ch_1_Glob = 'A';
  Bool_Glob = false;
} /* Proc_5 */
