Modifying Probability Distributions
===================================

This section provides a description of the housing characteristics and their dependencies and options.

A particular building within the building stock has a set of characteristics (e.g., level of wall insulation, type of lighting, vintage, and a variety of different schedules).  Each housing characteristic corresponds to a tab-separated value (tsv) file with the extension `.tsv`.  These housing characteristics files are found in the ``<project_folder>/housing_characteristics`` directory.  A housing characteristic defines the probability mass function (PMF) of that characteristic in the building stock. 

:math:`Pr(X=A_i) = P(A_i) > 0 \hspace{5mm} and \hspace{5mm} \sum_{A_i\in S_A} P(A_i) = 1 \hspace{5mm} for \hspace{5mm} i=1:n`

When sampling a discrete random variable :math:`X` to create a representative building, :math:`X` takes a particular **Option** :math:`A_i`.  All possible options are collected in the set :math:`S_A=\{A_0,A_1,...,A_n\}` and is size :math:`n`.  Since these are probabilities, the entries :math:`P(A_i)` must be greater than 0 and the probability of all possible options must sum to 1.  

For example, a set of options for a building's vintage (when the building was built) may be the following:

:math:`S_A = {<1950, 1950s, 1960s, 1970s, 1980s, 1990s, 2000s}.`

Then the probability mass function may look like the following:

+------------------+-------+-------+-------+-------+-------+-------+-------+
|    :math:`A_i`   | <1950 | 1950s | 1960s | 1970s | 1980s | 1990s | 2000s |
+==================+=======+=======+=======+=======+=======+=======+=======+
| :math:`P(X=A_i)` | 0.020 | 0.060 | 0.090 | 0.230 | 0.370 | 0.130 | 0.090 |
+------------------+-------+-------+-------+-------+-------+-------+-------+

Where the probability of a building having a given vintage in this example is

- 2% built before 1950, 
- 6% in the 1950s, 
- 9% in the 1960s, 
- 23% in the 1970s, 
- 37% in the 1980s, 
- 13% in the 1900s, and 
- 9% in the 2000s.

However, housing characteristics can have a **Dependency**, :math:`B_i`, to another housing characteristic.  All possible values of the dependency are collected in the set :math:`S_B = {B_0,B_1,...B_m}` which is size :math:`m`.  If the **Option** of interest :math:`A_j` and the **Dependency** :math:`B_i` is known to have occurred when sampling :math:`X` in the creation of a representative building, then conditional probability of :math:`A_j` given :math:`B_i` is usually written :math:`P(A_j|B_i)=P_{B_i}(A_j)`.

Using the example from before, the PMF of the vintage depends on location of the particular building stock (which is represented by EPW weather files). In this example the vintage housing characteristic is examined.  The first three lines in the ``<project_folder>/housing_characteristics/Vintage.tsv`` are shown in the table below.  

+-----------------------+-------------------------------------------------+-------+-------+-------+-------+-------+-------+-------+
|                       |     Location EPW (:math:`S_B`)                  | <1950 | 1950s | 1960s | 1970s | 1980s | 1990s | 2000s |
+-----------------------+-------------------------------------------------+-------+-------+-------+-------+-------+-------+-------+
| :math:`P(B_0|A_j)`    |     USA_FL_Key.West.Intl.AP.722010_TMY3.epw     | 0.02  | 0.06  | 0.09  | 0.23  | 0.37  | 0.13  | 0.09  |
+-----------------------+-------------------------------------------------+-------+-------+-------+-------+-------+-------+-------+
| :math:`P(B_1|A_j)`    |     USA_FL_Miami.Intl.AP.722020_TMY3.epw        | 0.05  | 0.13  | 0.13  | 0.18  | 0.17  | 0.18  | 0.16  |
+-----------------------+-------------------------------------------------+-------+-------+-------+-------+-------+-------+-------+

The vintage is dependent on the EPW location.  The vintage discrete PMF that uses the Key West International Airport weather file, :math:`B_0`, is defined by the following distribution: 

- 2% built before 1950, 
- 6% in the 1950s, 
- 9% in the 1960s, 
- 23% in the 1970s, 
- 37% in the 1980s, 
- 13% in the 1900s, and 
- 9% in the 2000s.

While the vintage PMF that uses the Miami International Airport weather file, :math:`B_1` is defined by the following distribution:

- 5% built before 1950, 
- 13% in the 1950s, 
- 9% in the 1960s, 
- 13% in the 1970s, 
- 18% in the 1980s, 
- 17% in the 1900s, and 
- 18% in the 2000s.

The **Options** can correspond to a Measure in OpenStudio or can be used as a **Dependency** for other housing characteristics.  For the list of available options for a given housing characteristic, see the ``resources/options_lookup.tsv`` file.  In this file the "Parameter Name" corresponds to the housing characteristic, the "Option Name" corresponds to an available option for the housing characteristic, the "Measure Dir" corresponds to the OpenStudio Measure being used, and the following columns correspond to different arguments needed by the OpenStudio Measure.  Each option used in the housing characteristics tsv files must be in this ``resources/options_lookup.tsv``. These options can be modified by the user to model their particular building stock.
