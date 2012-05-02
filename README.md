Cassandra Translator
====================

Translates from Datalog-C to Python. The Datalog-C is specific to the Cassandra system described in [Moritz Becker's thesis]([example link](http://research.microsoft.com/apps/pubs/default.aspx?id=76079). Currently a work in progress.

Usage
-----
Run translator.py

The generated rules will appear in the directory `ehr`.

Paper Abstract
--------------
__Improving the Specification and Implementation of EHR Policy Rules__

Arjun G. Menon and Yanhong A. Liu

Trust management policies are essential in decentralized systems in general and health care systems in particular, to preserve privacy of information and control access to resources.  [Moritz Becker's dissertation](http://www.cs.sunysb.edu/~stoller/cse592/becker05cassandra-thesis.pdf) [1] describes a system for distributed role-based access control for the UK's Electronic Health Record (EHR) service. In this system, sensitive user data and resources at every node in the network of hospitals and clinics are protected by certain entities which form a "protective layers" around those resources and controls access to them based on a policy defined using a policy definition language called Cassandra. Cassandra is a high-level logic rule language based on Datalog with constraints. The expressiveness of particular rules in Cassandra can be fine tuned by means of constraints.

While this national EHR policy in Cassandra is the largest of its kind that has been formally specified, it has two main aspects that need improvements.  The policy deals with all requirements concerning access control of patient-identifiable data, including legitimate relationships, patients restricting access, authenticated express consent, third-party consent, and workgroup management.  However, with a total of 375 rules in about 2000 lines of Cassandra, the entire policy was written as flat rules, because Cassandra does not support any organizing structure.   Also, all updates are encoded as two predicates that need special processing outside the logic framework, because Cassandra does not support explicit update operations.

Our work presents a translation of the EHR policy rules from Cassandra to Python, an object-oriented programming language that supports high-level queries and updates.  Our object-oriented modeling overcomes the lack of modularity and update abilities in Cassandra.  It improves the extensibility and readability of the rules and at the same time leads to a fully executable policy specification, which can be used as a prototype for automatic policy enforcement as well as for testing and experiments.  The main challenges were to add structures to the flat policy rules in Cassandra and to make implicit updates explicit.

To assist in the translation, we developed a tool that automatically translates a large part of the EHR specification from Cassandra to Python.  The translation looks for related rules based on what roles are activated and deactivated by the rules,  and places them within role classes in the translated object-oriented model for the policy. It also translates the logic rules into high-level queries and updates over objects and sets as much as possible. The translator can automatically translate 90% of the policy rules from Cassandra to Python, leaving a few untranslated rules marked out for human translation. The rules left untranslated are complex rules that involve large nested tuple data structures that need to be re-organized and placed in separate classes.

The translated EHR policy is organized into four modules----Spine, Patient Demographic Service, Hospital, and Hospital's Registration Authority----based on the numbering of the rules expressed in Cassandra.  These modules better model the four different components of the EHR service.  A class is created for each role, for a total of 58 parameterized roles in the EHR policy, including 25 in Spine, 7 in Patient Demographic Service, 31 in Hospital, and 7 in Hospital's Registration Authority.  The parameters of the roles are naturally expressed as attributes of the corresponding role classes.  The total number of methods in the resulting object-oriented model of the EHR policy is basically  the same as the number of rules.

Overall, this work provides important improvements to this large EHR policy that allow it to be executed easily and used for functionality testing, correctness validation, and performance evaluation.

[1]  Moritz Y. Becker, Cassandra: flexible trust management and its application to electronic health records. Ph.D. Dissertation, University of Cambridge, Trinity College,
October 2005.

Arjun G. Menon is a senior majoring in Computer Science at Stony Brook University.
Y. Annie Liu is a Professor in Computer Science at Stony Brook University.
