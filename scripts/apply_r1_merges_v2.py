#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_r1_merges_v2.py — verified clean MERGES list."""
import os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4 = os.path.join(REPO, "data", "text-files", "v4", "grc")

MERGES = [
    ('02-mark/mark-01.txt', '1:26', 'καὶ φωνῆσαν φωνῇ μεγάλῃ', 'καὶ σπαράξαν αὐτὸν τὸ πνεῦμα τὸ ἀκάθαρτον'),
    ('02-mark/mark-01.txt', '1:40', 'λέγων αὐτῷ', 'Καὶ ἔρχεται πρὸς αὐτὸν λεπρὸς παρακαλῶν αὐτὸν καὶ γονυπετῶν'),
    ('02-mark/mark-02.txt', '2:12', 'λέγοντας', 'καὶ δοξάζειν τὸν θεὸν'),
    ('02-mark/mark-03.txt', '3:5', 'συλλυπούμενος ἐπὶ τῇ πωρώσει τῆς καρδίας αὐτῶν,', 'καὶ περιβλεψάμενος αὐτοὺς μετʼ ὀργῆς,'),
    ('02-mark/mark-05.txt', '5:23', 'λέγων', 'καὶ παρακαλεῖ αὐτὸν πολλὰ'),
    ('02-mark/mark-05.txt', '5:30', 'ἐπιστραφεὶς ἐν τῷ ὄχλῳ', 'καὶ εὐθὺς ὁ Ἰησοῦς ἐπιγνοὺς ἐν ἑαυτῷ τὴν ἐξ αὐτοῦ δύναμιν ἐξελθοῦσαν'),
    ('02-mark/mark-05.txt', '5:35', 'λέγοντες', 'ἔρχονται ἀπὸ τοῦ ἀρχισυναγώγου'),
    ('02-mark/mark-06.txt', '6:41', 'ἀναβλέψας εἰς τὸν οὐρανὸν', 'καὶ λαβὼν τοὺς πέντε ἄρτους καὶ τοὺς δύο ἰχθύας'),
    ('02-mark/mark-07.txt', '7:1', 'ἐλθόντες ἀπὸ Ἱεροσολύμων', 'Καὶ συνάγονται πρὸς αὐτὸν οἱ Φαρισαῖοι καί τινες τῶν γραμματέων'),
    ('02-mark/mark-13.txt', '13:9', 'ἕνεκεν ἐμοῦ', 'καὶ ἐπὶ ἡγεμόνων καὶ βασιλέων σταθήσεσθε'),
    ('02-mark/mark-13.txt', '13:9', 'εἰς μαρτύριον αὐτοῖς.', 'καὶ ἐπὶ ἡγεμόνων καὶ βασιλέων σταθήσεσθε'),
    ('02-mark/mark-14.txt', '14:22', 'εὐλογήσας', 'λαβὼν ἄρτον'),
    ('02-mark/mark-14.txt', '14:23', 'εὐχαριστήσας', None),
    ('03-luke/luke-09.txt', '9:16', 'ἀναβλέψας εἰς τὸν οὐρανὸν', 'λαβὼν δὲ τοὺς πέντε ἄρτους καὶ τοὺς δύο ἰχθύας'),
    ('06-rom/rom-01.txt', '1:1', 'ἀφωρισμένος εἰς εὐαγγέλιον θεοῦ', 'κλητὸς ἀπόστολος,'),
    ('06-rom/rom-01.txt', '1:3', 'περὶ τοῦ υἱοῦ αὐτοῦ,', 'τοῦ γενομένου ἐκ σπέρματος Δαυὶδ κατὰ σάρκα,'),
    ('06-rom/rom-02.txt', '2:2', 'κατὰ ἀλήθειαν ἐπὶ τοὺς τὰ τοιαῦτα πράσσοντας.', 'οἴδαμεν δὲ ὅτι τὸ κρίμα τοῦ θεοῦ ἐστιν'),
    ('06-rom/rom-03.txt', '3:21', 'μαρτυρουμένη ὑπὸ τοῦ νόμου καὶ τῶν προφητῶν,', 'Νυνὶ δὲ χωρὶς νόμου δικαιοσύνη θεοῦ πεφανέρωται,'),
    ('06-rom/rom-03.txt', '3:26', 'καὶ δικαιοῦντα τὸν ἐκ πίστεως Ἰησοῦ.', None),
    ('06-rom/rom-04.txt', '4:12', 'ἀλλὰ καὶ τοῖς στοιχοῦσιν τοῖς ἴχνεσιν τῆς ἐν ἀκροβυστίᾳ πίστεως τοῦ πατρὸς ἡμῶν Ἀβραάμ.', 'καὶ πατέρα περιτομῆς τοῖς οὐκ ἐκ περιτομῆς μόνον'),
    ('06-rom/rom-04.txt', '4:24', 'ἐπὶ τὸν ἐγείραντα Ἰησοῦν τὸν κύριον ἡμῶν ἐκ νεκρῶν,', 'οἷς μέλλει λογίζεσθαι, τοῖς πιστεύουσιν'),
    ('06-rom/rom-05.txt', '5:1', 'διὰ τοῦ κυρίου ἡμῶν Ἰησοῦ Χριστοῦ,', 'εἰρήνην ἔχομεν πρὸς τὸν θεὸν'),
    ('06-rom/rom-05.txt', '5:14', 'καὶ ἐπὶ τοὺς μὴ ἁμαρτήσαντας ἐπὶ τῷ ὁμοιώματι τῆς παραβάσεως Ἀδάμ,', 'ἀλλὰ ἐβασίλευσεν ὁ θάνατος ἀπὸ Ἀδὰμ μέχρι Μωϋσέως'),
    ('06-rom/rom-08.txt', '8:20', 'ἀλλὰ διὰ τὸν ὑποτάξαντα, ἐφʼ ἑλπίδι', 'οὐχ ἑκοῦσα'),
    ('06-rom/rom-13.txt', '13:4', 'εἰς ὀργὴν τῷ τὸ κακὸν πράσσοντι.', 'θεοῦ γὰρ διάκονός ἐστιν, ἔκδικος'),
    ('06-rom/rom-13.txt', '13:6', 'εἰς αὐτὸ τοῦτο προσκαρτεροῦντες.', 'λειτουργοὶ γὰρ θεοῦ εἰσιν'),
    ('08-2cor/2cor-08.txt', '8:24', 'εἰς αὐτοὺς ἐνδεικνύμενοι εἰς πρόσωπον τῶν ἐκκλησιῶν.', 'τὴν οὖν ἔνδειξιν τῆς ἀγάπης ὑμῶν καὶ ἡμῶν καυχήσεως ὑπὲρ ὑμῶν'),
    ('09-gal/gal-01.txt', '1:15', 'καὶ καλέσας διὰ τῆς χάριτος αὐτοῦ', 'ὅτε δὲ εὐδόκησεν ὁ ἀφορίσας με ἐκ κοιλίας μητρός μου'),
    ('09-gal/gal-04.txt', '4:9', 'μᾶλλον δὲ γνωσθέντες ὑπὸ θεοῦ,', 'νῦν δὲ γνόντες θεόν,'),
    ('10-eph/eph-01.txt', '1:17', 'ἐν ἐπιγνώσει αὐτοῦ,', None),
    ('10-eph/eph-01.txt', '1:19', 'εἰς ἡμᾶς τοὺς πιστεύοντας', None),
    ('10-eph/eph-01.txt', '1:19', 'κατὰ τὴν ἐνέργειαν τοῦ κράτους τῆς ἰσχύος αὐτοῦ', None),
    ('10-eph/eph-01.txt', '1:21', 'ἀλλὰ καὶ ἐν τῷ μέλλοντι·', 'οὐ μόνον ἐν τῷ αἰῶνι τούτῳ'),
    ('10-eph/eph-03.txt', '3:9', 'ἐν τῷ θεῷ τῷ τὰ πάντα κτίσαντι,', None),
    ('10-eph/eph-03.txt', '3:20', 'κατὰ τὴν δύναμιν τὴν ἐνεργουμένην ἐν ἡμῖν,', None),
    ('11-phil/phil-01.txt', '1:1', 'σὺν ἐπισκόποις καὶ διακόνοις·', 'τοῖς οὖσιν ἐν Φιλίπποις'),
    ('12-col/col-01.txt', '1:3', 'περὶ ὑμῶν προσευχόμενοι,', 'Εὐχαριστοῦμεν τῷ θεῷ πατρὶ τοῦ κυρίου ἡμῶν Ἰησοῦ Χριστοῦ'),
    ('12-col/col-01.txt', '1:11', 'κατὰ τὸ κράτος τῆς δόξης αὐτοῦ', None),
    ('12-col/col-01.txt', '1:11', 'εἰς πᾶσαν ὑπομονὴν καὶ μακροθυμίαν', None),
    ('12-col/col-01.txt', '1:11', 'μετὰ χαρᾶς,', None),
    ('15-1tim/1tim-01.txt', '1:12', 'θέμενος εἰς διακονίαν,', None),
    ('15-1tim/1tim-06.txt', '6:3', 'ὑγιαίνουσι λόγοις, τοῖς τοῦ κυρίου ἡμῶν Ἰησοῦ Χριστοῦ,', None),
    ('14-2thess/2thess-01.txt', '1:7', 'ἀπʼ οὐρανοῦ', None),
    ('14-2thess/2thess-03.txt', '3:11', 'ἀλλὰ περιεργαζομένους·', None),
    ('16-2tim/2tim-01.txt', '1:3', 'ἐν καθαρᾷ συνειδήσει,', None),
    ('16-2tim/2tim-01.txt', '1:3', 'ἐν ταῖς δεήσεσίν μου,', None),
    ('16-2tim/2tim-01.txt', '1:3', 'νυκτὸς καὶ ἡμέρας', None),
    ('16-2tim/2tim-03.txt', '3:13', 'πλανῶντες καὶ πλανώμενοι.', None),
    ('19-heb/heb-03.txt', '3:18', 'εἰ μὴ τοῖς ἀπειθήσασιν;', None),
    ('19-heb/heb-07.txt', '7:18', 'διὰ τὸ αὐτῆς ἀσθενὲς καὶ ἀνωφελές,', None),
    ('19-heb/heb-09.txt', '9:19', 'μετὰ ὕδατος καὶ ἐρίου κοκκίνου καὶ ὑσσώπου', 'λαβὼν τὸ αἷμα τῶν μόσχων'),
    ('19-heb/heb-13.txt', '13:21', 'διὰ Ἰησοῦ Χριστοῦ,', 'ποιῶν ἐν ἡμῖν τὸ εὐάρεστον ἐνώπιον αὐτοῦ'),
    ('21-1pet/1pet-01.txt', '1:22', 'ἐν τῇ ὑπακοῇ τῆς ἀληθείας', None),
    ('21-1pet/1pet-01.txt', '1:22', 'εἰς φιλαδελφίαν ἀνυπόκριτον,', None),
    ('21-1pet/1pet-03.txt', '3:1', 'διὰ τῆς τῶν γυναικῶν ἀναστροφῆς', 'ἄνευ λόγου κερδηθήσονται'),
    ('21-1pet/1pet-03.txt', '3:16', 'ἀλλὰ μετὰ πραΰτητος καὶ φόβου,', 'συνείδησιν ἔχοντες ἀγαθήν,'),
    ('22-2pet/2pet-03.txt', '3:11', 'ἐν ἁγίαις ἀναστροφαῖς καὶ εὐσεβείαις,', 'ποταποὺς δεῖ ὑπάρχειν ὑμᾶς'),
    ('19-heb/heb-04.txt', '4:15', 'καθʼ ὁμοιότητα χωρὶς ἁμαρτίας.', 'πεπειρασμένον δὲ κατὰ πάντα'),
    ('05-acts/acts-14.txt', '14:14', 'κράζοντες ¹⁵καὶ λέγοντες·', None),
    ('03-luke/luke-24.txt', '24:47', 'ἀρξάμενοι ἀπὸ Ἰερουσαλήμ·', None),
    ('04-john/john-07.txt', '7:42', 'ὅτι ἐκ τοῦ σπέρματος Δαυίδ, καὶ ἀπὸ Βηθλέεμ τῆς κώμης', None),
    ('03-luke/luke-20.txt', '20:28', 'λέγοντες·', None),
    ('02-mark/mark-02.txt', '2:3', 'αἰρόμενον ὑπὸ τεσσάρων.', None),
    ('01-matt/matt-15.txt', '15:30', 'ἔχοντες μεθʼ ἑαυτῶν', None),
    ('01-matt/matt-26.txt', '26:26', 'καὶ εὐλογήσας', None),
    ('01-matt/matt-26.txt', '26:27', 'καὶ εὐχαριστήσας', None),
    ('01-matt/matt-26.txt', '26:47', 'μετὰ μαχαιρῶν καὶ ξύλων', None),
    ('01-matt/matt-26.txt', '26:47', 'ἀπὸ τῶν ἀρχιερέων καὶ πρεσβυτέρων τοῦ λαοῦ.', None),
    ('01-matt/matt-27.txt', '27:48', 'πλήσας τε ὄξους', None),
    ('01-matt/matt-27.txt', '27:48', 'καὶ περιθεὶς καλάμῳ', None),
    ('06-rom/rom-02.txt', '2:8', 'πειθομένοις δὲ τῇ ἀδικίᾳ', None),
    ('06-rom/rom-05.txt', '5:6', 'ἔτι κατὰ καιρὸν', None),
    ('06-rom/rom-06.txt', '6:13', 'ὡσεὶ ἐκ νεκρῶν ζῶντας', None),
    ('06-rom/rom-08.txt', '8:4', 'ἐν ἡμῖν τοῖς μὴ κατὰ σάρκα περιπατοῦσιν ἀλλὰ κατὰ πνεῦμα·', None),
    ('06-rom/rom-11.txt', '11:33', 'καὶ σοφίας', None),
    ('06-rom/rom-11.txt', '11:33', 'καὶ γνώσεως θεοῦ·', None),
    ('07-1cor/1cor-01.txt', '1:1', 'διὰ θελήματος θεοῦ', None),
    ('07-1cor/1cor-01.txt', '1:2', 'ἐν παντὶ τόπῳ αὐτῶν καὶ ἡμῶν·', None),
    ('07-1cor/1cor-04.txt', '4:11', 'ἄχρι τῆς ἄρτι ὥρας', None),
    ('07-1cor/1cor-11.txt', '11:25', 'λέγων·', None),
    ('07-1cor/1cor-14.txt', '14:21', 'ὅτι Ἐν ἑτερογλώσσοις', None),
    ('07-1cor/1cor-16.txt', '16:6', 'πρὸς ὑμᾶς δὲ τυχὸν', None),
    ('08-2cor/2cor-01.txt', '1:1', 'διὰ θελήματος θεοῦ', None),
    ('08-2cor/2cor-01.txt', '1:6', 'ὑπὲρ τῆς ὑμῶν παρακλήσεως καὶ σωτηρίας·', None),
    ('08-2cor/2cor-01.txt', '1:9', 'ἀλλʼ ἐπὶ τῷ θεῷ τῷ ἐγείροντι τοὺς νεκρούς·', None),
    ('08-2cor/2cor-01.txt', '1:23', 'ὅτι φειδόμενος ὑμῶν', None),
    ('08-2cor/2cor-04.txt', '4:13', 'κατὰ τὸ γεγραμμένον·', None),
    ('08-2cor/2cor-10.txt', '10:2', 'ὡς κατὰ σάρκα περιπατοῦντας.', None),
    ('12-col/col-04.txt', '4:12', 'καὶ πεπληροφορημένοι ἐν παντὶ θελήματι τοῦ θεοῦ.', None),
    ('14-2thess/2thess-01.txt', '1:7', 'μετʼ ἀγγέλων δυνάμεως αὐτοῦ', None),
    ('27-rev/rev-04.txt', '4:6', 'Καὶ ἐν μέσῳ τοῦ θρόνου', None),
    ('27-rev/rev-04.txt', '4:6', 'καὶ κύκλῳ τοῦ θρόνου', None),
    ('27-rev/rev-13.txt', '13:1', 'καὶ ἐπὶ τῶν κεράτων αὐτοῦ δέκα διαδήματα,', None),
    ('27-rev/rev-13.txt', '13:1', 'καὶ ἐπὶ τὰς κεφαλὰς αὐτοῦ ὀνόματα βλασφημίας.', None),
]


VERSE_RE = re.compile(r"^\d+:\d+\s*$")


def normalize(s):
    return re.sub(r"\s+", " ", s).strip()


def find_verse(lines, ref):
    start = None
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s == ref:
            start = i + 1
        elif start is not None and VERSE_RE.match(s):
            return start, i
    if start is not None:
        return start, len(lines)
    return None, None


def find_line(lines, lo, hi, target):
    tn = normalize(target)
    for i in range(lo, hi):
        ln = normalize(lines[i])
        if ln == tn or ln.startswith(tn):
            return i
    return -1


def apply_one(lines, ref, src, tgt):
    lo, hi = find_verse(lines, ref)
    if lo is None:
        return False, f"verse {ref} not found"
    src_idx = find_line(lines, lo, hi, src)
    if src_idx == -1:
        return False, f"src not found: {src[:40]}"
    if tgt:
        tgt_idx = find_line(lines, lo, hi, tgt)
        if tgt_idx == -1:
            return False, f"tgt not found: {tgt[:40]}"
        if tgt_idx == src_idx:
            return False, "tgt == src"
    else:
        # Try preceding line first
        tgt_idx = -1
        for k in range(src_idx - 1, lo - 1, -1):
            n = normalize(lines[k])
            if n and not VERSE_RE.match(n):
                tgt_idx = k
                break
        # Fall back to next line if no preceding (src is first line of verse)
        if tgt_idx == -1:
            for k in range(src_idx + 1, hi):
                n = normalize(lines[k])
                if n and not VERSE_RE.match(n):
                    tgt_idx = k
                    break
        if tgt_idx == -1:
            return False, "no merge target in verse"
    earlier = min(src_idx, tgt_idx)
    later = max(src_idx, tgt_idx)
    lines[earlier] = lines[earlier].rstrip("\n").rstrip() + " " + lines[later].rstrip("\n").lstrip() + "\n"
    del lines[later]
    return True, "ok"


def main():
    dry = "--dry-run" in sys.argv
    by_file = {}
    for f, r, s, t in MERGES:
        by_file.setdefault(f, []).append((r, s, t))
    applied = 0
    failed = []
    for fp, entries in sorted(by_file.items()):
        full = os.path.join(V4, fp)
        if not os.path.exists(full):
            for r, s, t in entries:
                failed.append((fp, r, "file not found"))
            continue
        with open(full, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
        applied_in_file = 0
        for r, s, t in entries:
            ok, reason = apply_one(lines, r, s, t)
            if ok:
                applied += 1
                applied_in_file += 1
            else:
                failed.append((fp, r, reason))
        if applied_in_file and not dry:
            with open(full, "w", encoding="utf-8") as fh:
                fh.writelines(lines)
        if applied_in_file:
            print(f"  {'[dry] ' if dry else ''}{fp}: {applied_in_file}")
    print(f"\n=== {applied} applied / {len(failed)} failed ===")
    for fp, r, rsn in failed[:30]:
        print(f"  FAIL {fp} {r}: {rsn}")


if __name__ == "__main__":
    main()
