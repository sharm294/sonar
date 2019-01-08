/*******************************************************************************
 * This allows macros to be expanded differently based on the values of the 
 * arguments. i.e. 
 * 
 * #define COMPARE_foo(x) x
 * #define COMPARE_bar(x) x
 * #define WRITE(key) \
    WHEN(EQUAL(key, foo))(WRITE_0)\
    WHEN(EQUAL(key, bar))(READ_0)
 * ^ Here, the macro WRITE(key) will expand to another macro WRITE_0 if key is
 * equal to foo or to READ_0 if it is equal to bar. The COMPARE_xxx defines 
 * need to be specified for all options and therefore other define statements 
 * cannot start with COMPARE_
 * 
 * Reference: https://github.com/pfultz2/Cloak/wiki/C-Preprocessor-tricks,-tips,-and-idioms
*******************************************************************************/

#define CAT(a, ...) PRIMITIVE_CAT(a, __VA_ARGS__)
#define PRIMITIVE_CAT(a, ...) a ## __VA_ARGS__

#define IIF(c) PRIMITIVE_CAT(IIF_, c)
#define IIF_0(t, ...) __VA_ARGS__
#define IIF_1(t, ...) t

#define COMPL(b) PRIMITIVE_CAT(COMPL_, b)
#define COMPL_0 1
#define COMPL_1 0

#define BITAND(x) PRIMITIVE_CAT(BITAND_, x)
#define BITAND_0(y) 0
#define BITAND_1(y) y

#define CHECK_N(x, n, ...) n
#define CHECK(...) CHECK_N(__VA_ARGS__, 0,)
#define PROBE(x) x, 1,

#define IS_PAREN(x) CHECK(IS_PAREN_PROBE x)
#define IS_PAREN_PROBE(...) PROBE(~)

#define NOT(x) CHECK(PRIMITIVE_CAT(NOT_, x))
#define NOT_0 PROBE(~)

#define BOOL(x) COMPL(NOT(x))
#define IF(c) IIF(BOOL(c))

#define EAT(...)
#define EXPAND(...) __VA_ARGS__
#define WHEN(c) IF(c)(EXPAND, EAT)

#define EXPAND(...) __VA_ARGS__

#define PRIMITIVE_COMPARE(x, y) IS_PAREN \
    ( COMPARE_ ## x ( COMPARE_ ## y) (()) )

#define IS_COMPARABLE(x) IS_PAREN( CAT(COMPARE_, x) (()) )

#define NOT_EQUAL(x, y) \
    IIF(BITAND(IS_COMPARABLE(x))(IS_COMPARABLE(y)) ) ( \
        PRIMITIVE_COMPARE, 1 EAT \
    )(x, y)

#define EQUAL(x, y) COMPL(NOT_EQUAL(x, y))
