# Spatial R-Trees

Υλοποίηση R-Tree για την εργασία **Διαχείριση Σύνθετων Δεδομένων**.  

Το project περιλαμβάνει δύο βασικά μέρη:
1. **Bulk Loading** — Κατασκευή R-Tree με ταξινόμηση MBRs βάσει Z-order (Morton code).
2. **Range Queries** — Αποτίμηση ερωτήσεων εύρους (filter step) πάνω στο R-Tree.

---

## 📂 Δομή φακέλων

src/ # Κώδικας (R_tree_bulk.py, range_queries.py)
data/ # Αρχεία εισόδου (coords.txt, offsets.txt, Rqueries.txt)
output/ # Έξοδοι (π.χ. Rtree.txt, levels.txt, query_results.txt)
docs/ # Συνοδευτικά έγγραφα (Report.pdf)

### Μέρος 1 — Κατασκευή R-Tree

Δέχεται `offsets.txt` και `coords.txt` και παράγει `Rtree.txt`.

python src/R_tree_bulk.py data/offsets.txt data/coords.txt > output/levels.txt

Δημιουργεί:

output/Rtree.txt με όλους τους κόμβους του δέντρου.

Στο stdout εμφανίζει "[N] nodes at level [L]" για κάθε επίπεδο.

### Μέρος 2 — Range Queries

Δέχεται Rtree.txt και Rqueries.txt και τυπώνει αποτελέσματα.

python src/range_queries.py output/Rtree.txt data/Rqueries.txt > output/query_results.txt

Κάθε γραμμή έχει μορφή:

0 (7): 2527,2712,8371,5042,7080,7656,7944

όπου:

0 = αριθμός γραμμής ερώτησης

(7) = αριθμός αποτελεσμάτων

μετά ακολουθούν τα ids των αντικειμένων που τέμνονται με το παράθυρο ερώτησης.
