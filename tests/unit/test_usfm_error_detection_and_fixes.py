import pytest
import unittest
from doc.domain.usfm_error_detection_and_fixes import (
    remove_null_bytes_and_control_characters,
    fix_dot_after_verse_number,
    fix_usfm,
    fix_verse_marker_without_v,
    fix_missing_space_before_number,
    fix_missing_space_after_number,
    fix_missing_space_before_verse_marker,
    fix_standalone_verse_numbers,
    fix_space_after_section_marker,
    replace_n_with_v,
    replace_cc_with_c,
)


class USFMErrorDetection(unittest.TestCase):
    maxDiff = None

    @pytest.mark.usfm_fixes
    def test_fix_dot_after_verse_number(self) -> None:
        self.assertEqual(
            fix_dot_after_verse_number(r"\v 1.Some text."), r"\v 1 Some text."
        )
        self.assertEqual(
            fix_dot_after_verse_number(r"\v 2.Another verse."), r"\v 2 Another verse."
        )
        self.assertEqual(
            fix_dot_after_verse_number(r"\v 2 .Another verse."), r"\v 2 Another verse."
        )
        self.assertEqual(
            fix_dot_after_verse_number(r"\v 2 . Another verse."),
            r"\v 2 Another verse.",
        )
        self.assertNotEqual(
            fix_dot_after_verse_number(r"\v 3. \v 4. Text."), r"\v 3 \v 4 Text."
        )
        self.assertEqual(
            fix_dot_after_verse_number(r"\v 5.Something."), r"\v 5 Something."
        )
        self.assertEqual(
            fix_dot_after_verse_number(r"\v 6 Some text."), r"\v 6 Some text."
        )
        self.assertEqual(
            # gwg_reg_2jn
            fix_dot_after_verse_number(
                r"\v 1. Ba yuku wekam tala ba na,ah i yanzangulah, yuka bi yidi wei ɓalang , ban i ninsim yau, ii yau kala ii nin a lanɓa. \v 2 . Wei balang ka wei Nyiibilah ba tahfahza ibi lah ding. \v 3 . Kacho sacha i ninvii i saetam tafahza ɓafuh tah gabi ii bah Yeeso Krisi kala wii tahgabi wei balang i bah yidibe."
            ),
            r"\v 1 Ba yuku wekam tala ba na,ah i yanzangulah, yuka bi yidi wei ɓalang , ban i ninsim yau, ii yau kala ii nin a lanɓa. \v 2 Wei balang ka wei Nyiibilah ba tahfahza ibi lah ding. \v 3 Kacho sacha i ninvii i saetam tafahza ɓafuh tah gabi ii bah Yeeso Krisi kala wii tahgabi wei balang i bah yidibe.",
        )

    @pytest.mark.usfm_fixes
    def test_fix_verse_marker_without_v(self) -> None:
        self.assertEqual(
            fix_verse_marker_without_v(r"\1.Some text."), r"\v 1 Some text."
        )
        self.assertEqual(
            fix_verse_marker_without_v(r"\1. Some text."), r"\v 1 Some text."
        )
        self.assertEqual(
            fix_verse_marker_without_v(r"\1 Some text."), r"\v 1 Some text."
        )
        self.assertEqual(
            fix_verse_marker_without_v(
                # gwg php
                r""""\c 1\cl Chapter 1
\1.Bulus I Timoti zab I ya nwohlo Yeso,wala be yauka ii Raman loi we Almasihu Yeso kai Filibi la ɓa ,I yauka la na ɓi wekhem ii ya ɗinkin la.\2.Na ni nha Malang ah I ɓa lah i satem ba fuh tahgaɓi ya Yeso Almasihu la.
\3. Vinse na man kpha fuhm ka nan zii bagaba.\4.Vinse we ba linwabung ɓuocnham la,la bagaba se ,Ii nyin faram la Neman li nwah buock.\5.Na man kha fuh la bai ba gamza gabq we bai fuh la bepiu la wulah vii a jekang.\6.In bi yang la bai ninka,Yuka be pi ba ba chonin ala we ba la ba ,au tarta vii kau u gama wala vii ba wai Yeso Almasihu."""
            ),
            r""""\c 1\cl Chapter 1
\v 1 Bulus I Timoti zab I ya nwohlo Yeso,wala be yauka ii Raman loi we Almasihu Yeso kai Filibi la ɓa ,I yauka la na ɓi wekhem ii ya ɗinkin la.\v 2 Na ni nha Malang ah I ɓa lah i satem ba fuh tahgaɓi ya Yeso Almasihu la.
\v 3 Vinse na man kpha fuhm ka nan zii bagaba.\v 4 Vinse we ba linwabung ɓuocnham la,la bagaba se ,Ii nyin faram la Neman li nwah buock.\v 5 Na man kha fuh la bai ba gamza gabq we bai fuh la bepiu la wulah vii a jekang.\v 6 In bi yang la bai ninka,Yuka be pi ba ba chonin ala we ba la ba ,au tarta vii kau u gama wala vii ba wai Yeso Almasihu.""",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(r"1 Some text."),
            r"\v 1 Some text.",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers2(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(r"1 Some text. 2 This is more text."),
            r"\v 1 Some text. \v 2 This is more text.",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers3(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(r"\v 1 Some text. \v 2 This is more text."),
            r"\v 1 Some text. \v 2 This is more text.",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers4(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(r"1 Some text. \v 2 This is more text."),
            r"\v 1 Some text. \v 2 This is more text.",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers5(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(r"\c 1 Some text. \v 1 This is more text."),
            r"\c 1 Some text. \v 1 This is more text.",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers6(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(r"\1 Some text. \2 This is more text."),
            r"\1 Some text. \2 This is more text.",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers7(self) -> None:
        actual = fix_standalone_verse_numbers(
            # iba-x-ibanempran, col
            fix_missing_space_after_number(
                fix_missing_space_before_number(
                    r"""
1Laban aku betemu aku. 2Aku dekaka, lalu nemu misteri Allah Taala, iya nya Kristus Empu,3 ke enggau penemu dilalaika.
                """.strip()
                )
            )
        )
        expected = r"""
\v 1 Laban aku betemu aku. \v 2 Aku dekaka, lalu nemu misteri Allah Taala, iya nya Kristus Empu, \v 3 ke enggau penemu dilalaika.
""".strip()
        # print("Actual Output:")
        # print(repr(actual))
        # print("Expected Output:")
        # print(repr(expected))
        self.assertEqual(actual, expected)

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers8(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(
                fix_missing_space_after_number(
                    r"""
1Kita ke anak, ngasika apai indai kita dalam Tuhan, laban utai nya ngena. 2 “Bebasaka apai enggau indai nuan” - nya terubah-rubah pesan ti disempulang enggau semaya: 3 “ngambika nuan mujur, sereta panjai umur nguan menua.”
"""
                )
            ),
            r"""
\v 1 Kita ke anak, ngasika apai indai kita dalam Tuhan, laban utai nya ngena. \v 2 “Bebasaka apai enggau indai nuan” - nya terubah-rubah pesan ti disempulang enggau semaya: \v 3 “ngambika nuan mujur, sereta panjai umur nguan menua.”
""",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers9(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(
                r"""
\v 8 وفلتين النسوان القبر سريع وهن خايفات وفارحات قوي ، وكانين يجرين علميد يبشرين الطلاب \v 9 فلقيهن عيسى في الطريق وقال لهن :(السلام عليكما) وقربين منه ومسكين ارجله وسجدين له \v 10 فقال لهن عيسى :(لا تخافينش ، سيرين لإخوتي وقولين لهم انهم يسيروا للجليل ، وهاناك عيبسروني)
"""
            ),
            r"""
\v 8 وفلتين النسوان القبر سريع وهن خايفات وفارحات قوي ، وكانين يجرين علميد يبشرين الطلاب \v 9 فلقيهن عيسى في الطريق وقال لهن :(السلام عليكما) وقربين منه ومسكين ارجله وسجدين له \v 10 فقال لهن عيسى :(لا تخافينش ، سيرين لإخوتي وقولين لهم انهم يسيروا للجليل ، وهاناك عيبسروني)
""",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers10(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(
                r"""\v 15 وأليود ولد أليعازر \li1 وأليعازر ولد متان \li1 ومتان ولد يعقوب \li1 \v 16 ويعقوب ولد يوسف رجل مريم اللي ولدت عيسى اللي يسموه المسيح \li4 \v 17 ويطلع مجموع الأجيال من إبراهيم إلى داود 14 جيل ومن داود إلى الأسر البابلي 14 جيل ومن الأسر البابلي إلى المسيح 14 جيل"""
            ),
            r"""\v 15 وأليود ولد أليعازر \li1 وأليعازر ولد متان \li1 ومتان ولد يعقوب \li1 \v 16 ويعقوب ولد يوسف رجل مريم اللي ولدت عيسى اللي يسموه المسيح \li4 \v 17 ويطلع مجموع الأجيال من إبراهيم إلى داود 14 جيل ومن داود إلى الأسر البابلي 14 جيل ومن الأسر البابلي إلى المسيح 14 جيل""",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers11(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(
                r"""\v 1 This is a verse \v2 this is another verse 3 and this verse too 4 and another as well"""
            ),
            r"""\v 1 This is a verse \v2 this is another verse \v 3 and this verse too \v 4 and another as well""",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers12(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(
                r"""\v 1 This is a verse \v2 this is another verse 3 and this verse too 3 and another as well"""
            ),
            r"""\v 1 This is a verse \v2 this is another verse 3 and this verse too 3 and another as well""",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers13(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(
                fix_missing_space_after_number(
                    r"""
1 Ari Jude, menyadi James, ke nyadi ulun Jesus Kristus,

Ngagai orang ke udah dikangau, ke dikerinduka Allah Taala ti Apai, sereta dijaga Jesus Kristus:

2Awakka pengasih, pemaik enggau pengerindu nambah-menambah diberi ngagai kita.
Pengajar Ti Pelesu
3Menyadi, lebuh aku benung gagit ati nyendiaka diri nulis ngagai kita pasal pengelepas ti dikembuan semua kitai, aku ngira diri enda tau enda nulis ngagai kita minta kita bebendar gawa ke pengarap ti udah diberi sekali aja ngagai nembiak Tuhan. 4 Laban sekeda orang udah belalai enselitka diri tama ngagai bala kitai. Sida endang lama udah diletak deka diukum laban sida enda nangika Allah Taala. Sida nyarutka pesan pasal pengasih Allah Taala, lalu ngaga nya nyadika peluang kena sida ngereja pengawa ti kamah, lalu enggai ngaku Tuan enggau Tuhan kitai, Jesus Kristus, ti siku aja.
5 Diatu aku deka ngasuh kita ngingatka tu, taja pen kita udah nemu semua utai tu, iya nya, Tuhan udah ngelepaska orang Israel ari menua Ejip, tang udah nya, Iya munuh sida ke enda arap. 6Kingatka melikat ke enda nitihka sekat hak sida, tang ninggalka endur alai sida diau. Iya udah nanchang sida ngena rantai lalu nyimpan sida dalam endur ti pemadu petang, ngambika sida diakim lebuh Hari Pechara.
7 Lalu kingatka mega Sodom enggau Gomorah, enggau nengeri ti ngelingi nengeri dua buah nya, ti ngereja ulah ti kamah, lalu nyarutka pengawa beleman. Sida diukum ngena api ti enda nemu padam, kena ngajar semua mensia.

8Orang tu pen baka nya mega. Sida ngamahka tubuh diri, enggai diperintah Allah Taala, lalu mechat utai idup ti bemulia di serega.
9 Indah tuai melikat ke benama Mikael deh enda berani mechat Sitan lebuh iya berebutka bangkai Moses enggau Sitan, tang semina nyebut, “Tuhan ngerara nuan!” 10Tang bala orang tu mechat semua utai ti enda ditemu sida reti. Lalu utai ti ditemu sida ngena pengasai, baka jelu ti enda nemu berunding, nya meh utai ti ngerusak sida. 11 Tulah meh sida! Sida niti jalai Kain, lalu ngereja penyalah ketegal duit baka penyalah ti dikereja Balaam, lalu sida dirusak baka Korah ke angkat ngelaban.
12Sida tu ngamahka gempuru kita lebuh kita beserumpu makai, laban sida enda nemu malu lebuh sida makai, lalu semina berundingka diri empu aja. Sida nya baka mua hari ti dipuputka ribut, tang nadai ngasuh hari ujan. Sida nya baka kayu ti nadai buah lebuh musin ruruh daun, mati dua kali, lalu dichabut. 13Sida nya baka gelumbang di tasik, ti ngayanka pupu ti ngasuh sida malu. Sida nya baka bintang ti terebai, ti deka dibuai ngagai endur ti pemadu petang ti disedia Allah Taala ke sida belama iya.
14 Enok, tujuh serak ari Adam, udah benabika pasal sida nya dulu kelia: “Peda kita, Tuhan datai enggau beribu-ribu iku bala melikat Iya ti kudus, 15deka ngakim semua mensia, lalu ngukum genap iku orang ketegal semua penyai ti udah dikereja sida, enggau ketegal semua jaku jai ti udah disebut orang ke bedosa, ke enda arapka Allah Taala, kena sida ngelaban Iya!”

16Orang nya seruran mutap, seruran nganu pangan diri. Sida nurutka pengingin sida ti kamah. Sida muji diri, lalu ngelangkungka orang kena sida ngambi ulih ba orang.
Jaku Tangkan Enggau Atur
17Tang kita, menyadi, enda tau enda ingatka utai ti udah dipadahka bala rasul Jesus Kristus Tuhan kitai sebedau utai nya nyadi. 18 Ku sida madah ngagai kita, “Ba hari ti penudi, orang ke ngelese deka datai, nurutka pengingin sida ti kamah.” 19Nya meh orang ke nyungkak orang beserekang penemu. Sida tu diperintah pengingin dunya, sereta nadai ngembuan Roh Kudus.
20Tang kita, menyadi, enda tau enda negapka pengarap kita ti pemadu kudus, lalu besampi nitihka iring Roh Kudus; 21meruan dalam pengerindu Allah Taala; nganti pengasih Jesus Kristus Tuhan kitai ti deka mai kitai ngagai pengidup ti meruan belama iya.
22Kasihka orang ke kakang ati; 23 Rampas sekeda orang ari api, lalu selamatka sida; kasihka sida ti bukai enggau ati ti nangi, datai ke kita nyau begedika gari ti udah dikena sida ngereja ulah ti kamah.
Sampi Puji
24Ngagai Iya ke ulih nagang kita rebah, lalu nyerahka kita nadai bepenyalah sereta enggau ati ti gaga ngagai Iya ke bemulia, 25ngagai Allah Taala ti siku aja ke nyadi Juruselamat kitai, beri meh puji, mulia, pengering, enggau kuasa, ulih Jesus Kristus Tuhan kitai, kenyau ari dulu kelia, ngagai diatu, enggau ke belama-lama iya! Amin.
        """
                )
            ),
            r"""
\v 1 Ari Jude, menyadi James, ke nyadi ulun Jesus Kristus,

Ngagai orang ke udah dikangau, ke dikerinduka Allah Taala ti Apai, sereta dijaga Jesus Kristus:

\v 2 Awakka pengasih, pemaik enggau pengerindu nambah-menambah diberi ngagai kita.
Pengajar Ti Pelesu
\v 3 Menyadi, lebuh aku benung gagit ati nyendiaka diri nulis ngagai kita pasal pengelepas ti dikembuan semua kitai, aku ngira diri enda tau enda nulis ngagai kita minta kita bebendar gawa ke pengarap ti udah diberi sekali aja ngagai nembiak Tuhan. \v 4 Laban sekeda orang udah belalai enselitka diri tama ngagai bala kitai. Sida endang lama udah diletak deka diukum laban sida enda nangika Allah Taala. Sida nyarutka pesan pasal pengasih Allah Taala, lalu ngaga nya nyadika peluang kena sida ngereja pengawa ti kamah, lalu enggai ngaku Tuan enggau Tuhan kitai, Jesus Kristus, ti siku aja.
\v 5 Diatu aku deka ngasuh kita ngingatka tu, taja pen kita udah nemu semua utai tu, iya nya, Tuhan udah ngelepaska orang Israel ari menua Ejip, tang udah nya, Iya munuh sida ke enda arap. \v 6 Kingatka melikat ke enda nitihka sekat hak sida, tang ninggalka endur alai sida diau. Iya udah nanchang sida ngena rantai lalu nyimpan sida dalam endur ti pemadu petang, ngambika sida diakim lebuh Hari Pechara.
\v 7 Lalu kingatka mega Sodom enggau Gomorah, enggau nengeri ti ngelingi nengeri dua buah nya, ti ngereja ulah ti kamah, lalu nyarutka pengawa beleman. Sida diukum ngena api ti enda nemu padam, kena ngajar semua mensia.

\v 8 Orang tu pen baka nya mega. Sida ngamahka tubuh diri, enggai diperintah Allah Taala, lalu mechat utai idup ti bemulia di serega.
\v 9 Indah tuai melikat ke benama Mikael deh enda berani mechat Sitan lebuh iya berebutka bangkai Moses enggau Sitan, tang semina nyebut, “Tuhan ngerara nuan!” \v 10 Tang bala orang tu mechat semua utai ti enda ditemu sida reti. Lalu utai ti ditemu sida ngena pengasai, baka jelu ti enda nemu berunding, nya meh utai ti ngerusak sida. \v 11 Tulah meh sida! Sida niti jalai Kain, lalu ngereja penyalah ketegal duit baka penyalah ti dikereja Balaam, lalu sida dirusak baka Korah ke angkat ngelaban.
\v 12 Sida tu ngamahka gempuru kita lebuh kita beserumpu makai, laban sida enda nemu malu lebuh sida makai, lalu semina berundingka diri empu aja. Sida nya baka mua hari ti dipuputka ribut, tang nadai ngasuh hari ujan. Sida nya baka kayu ti nadai buah lebuh musin ruruh daun, mati dua kali, lalu dichabut. \v 13 Sida nya baka gelumbang di tasik, ti ngayanka pupu ti ngasuh sida malu. Sida nya baka bintang ti terebai, ti deka dibuai ngagai endur ti pemadu petang ti disedia Allah Taala ke sida belama iya.
\v 14 Enok, tujuh serak ari Adam, udah benabika pasal sida nya dulu kelia: “Peda kita, Tuhan datai enggau beribu-ribu iku bala melikat Iya ti kudus, \v 15 deka ngakim semua mensia, lalu ngukum genap iku orang ketegal semua penyai ti udah dikereja sida, enggau ketegal semua jaku jai ti udah disebut orang ke bedosa, ke enda arapka Allah Taala, kena sida ngelaban Iya!”

\v 16 Orang nya seruran mutap, seruran nganu pangan diri. Sida nurutka pengingin sida ti kamah. Sida muji diri, lalu ngelangkungka orang kena sida ngambi ulih ba orang.
Jaku Tangkan Enggau Atur
\v 17 Tang kita, menyadi, enda tau enda ingatka utai ti udah dipadahka bala rasul Jesus Kristus Tuhan kitai sebedau utai nya nyadi. \v 18 Ku sida madah ngagai kita, “Ba hari ti penudi, orang ke ngelese deka datai, nurutka pengingin sida ti kamah.” \v 19 Nya meh orang ke nyungkak orang beserekang penemu. Sida tu diperintah pengingin dunya, sereta nadai ngembuan Roh Kudus.
\v 20 Tang kita, menyadi, enda tau enda negapka pengarap kita ti pemadu kudus, lalu besampi nitihka iring Roh Kudus; \v 21 meruan dalam pengerindu Allah Taala; nganti pengasih Jesus Kristus Tuhan kitai ti deka mai kitai ngagai pengidup ti meruan belama iya.
\v 22 Kasihka orang ke kakang ati; \v 23 Rampas sekeda orang ari api, lalu selamatka sida; kasihka sida ti bukai enggau ati ti nangi, datai ke kita nyau begedika gari ti udah dikena sida ngereja ulah ti kamah.
Sampi Puji
\v 24 Ngagai Iya ke ulih nagang kita rebah, lalu nyerahka kita nadai bepenyalah sereta enggau ati ti gaga ngagai Iya ke bemulia, \v 25 ngagai Allah Taala ti siku aja ke nyadi Juruselamat kitai, beri meh puji, mulia, pengering, enggau kuasa, ulih Jesus Kristus Tuhan kitai, kenyau ari dulu kelia, ngagai diatu, enggau ke belama-lama iya! Amin.
        """,
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers14(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(
                fix_missing_space_after_number(
                    r"""
1 Ari Jude, menyadi James, ke nyadi ulun Jesus Kristus,

Ngagai orang ke udah dikangau, ke dikerinduka Allah Taala ti Apai, sereta dijaga Jesus Kristus:

2Awakka pengasih, pemaik enggau pengerindu nambah-menambah diberi ngagai kita.
Pengajar Ti Pelesu
        """
                )
            ),
            r"""
\v 1 Ari Jude, menyadi James, ke nyadi ulun Jesus Kristus,

Ngagai orang ke udah dikangau, ke dikerinduka Allah Taala ti Apai, sereta dijaga Jesus Kristus:

\v 2 Awakka pengasih, pemaik enggau pengerindu nambah-menambah diberi ngagai kita.
Pengajar Ti Pelesu
        """,
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers15(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(
                fix_missing_space_after_number(
                    r"""
1 Ari Jude, menyadi James, ke nyadi ulun Jesus Kristus,

Ngagai orang ke udah dikangau, ke dikerinduka Allah Taala ti Apai, sereta dijaga Jesus Kristus:

2Awakka pengasih, pemaik enggau pengerindu nambah-menambah diberi ngagai kita.
Pengajar Ti Pelesu
3Menyadi, lebuh aku benung gagit ati nyendiaka diri nulis ngagai kita pasal pengelepas ti dikembuan semua kitai, aku ngira diri enda tau enda nulis ngagai kita minta kita bebendar gawa ke pengarap ti udah diberi sekali aja ngagai nembiak Tuhan. 4 Laban sekeda orang udah belalai enselitka diri tama ngagai bala kitai. Sida endang lama udah diletak deka diukum laban sida enda nangika Allah Taala. Sida nyarutka pesan pasal pengasih Allah Taala, lalu ngaga nya nyadika peluang kena sida ngereja pengawa ti kamah, lalu enggai ngaku Tuan enggau Tuhan kitai, Jesus Kristus, ti siku aja.
5 Diatu aku deka ngasuh kita ngingatka tu, taja pen kita udah nemu semua utai tu, iya nya, Tuhan udah ngelepaska orang Israel ari menua Ejip, tang udah nya, Iya munuh sida ke enda arap. 6Kingatka melikat ke enda nitihka sekat hak sida, tang ninggalka endur alai sida diau. Iya udah nanchang sida ngena rantai lalu nyimpan sida dalam endur ti pemadu petang, ngambika sida diakim lebuh Hari Pechara.
7 Lalu kingatka mega Sodom enggau Gomorah, enggau nengeri ti ngelingi nengeri dua buah nya, ti ngereja ulah ti kamah, lalu nyarutka pengawa beleman. Sida diukum ngena api ti enda nemu padam, kena ngajar semua mensia.
        """
                )
            ),
            r"""
\v 1 Ari Jude, menyadi James, ke nyadi ulun Jesus Kristus,

Ngagai orang ke udah dikangau, ke dikerinduka Allah Taala ti Apai, sereta dijaga Jesus Kristus:

\v 2 Awakka pengasih, pemaik enggau pengerindu nambah-menambah diberi ngagai kita.
Pengajar Ti Pelesu
\v 3 Menyadi, lebuh aku benung gagit ati nyendiaka diri nulis ngagai kita pasal pengelepas ti dikembuan semua kitai, aku ngira diri enda tau enda nulis ngagai kita minta kita bebendar gawa ke pengarap ti udah diberi sekali aja ngagai nembiak Tuhan. \v 4 Laban sekeda orang udah belalai enselitka diri tama ngagai bala kitai. Sida endang lama udah diletak deka diukum laban sida enda nangika Allah Taala. Sida nyarutka pesan pasal pengasih Allah Taala, lalu ngaga nya nyadika peluang kena sida ngereja pengawa ti kamah, lalu enggai ngaku Tuan enggau Tuhan kitai, Jesus Kristus, ti siku aja.
\v 5 Diatu aku deka ngasuh kita ngingatka tu, taja pen kita udah nemu semua utai tu, iya nya, Tuhan udah ngelepaska orang Israel ari menua Ejip, tang udah nya, Iya munuh sida ke enda arap. \v 6 Kingatka melikat ke enda nitihka sekat hak sida, tang ninggalka endur alai sida diau. Iya udah nanchang sida ngena rantai lalu nyimpan sida dalam endur ti pemadu petang, ngambika sida diakim lebuh Hari Pechara.
\v 7 Lalu kingatka mega Sodom enggau Gomorah, enggau nengeri ti ngelingi nengeri dua buah nya, ti ngereja ulah ti kamah, lalu nyarutka pengawa beleman. Sida diukum ngena api ti enda nemu padam, kena ngajar semua mensia.
        """,
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers16(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(
                fix_missing_space_after_number(
                    r"""
1 Ari Jude, menyadi James, ke nyadi ulun Jesus Kristus,

Ngagai orang ke udah dikangau, ke dikerinduka Allah Taala ti Apai, sereta dijaga Jesus Kristus:

2Awakka pengasih, pemaik enggau pengerindu nambah-menambah diberi ngagai kita.
Pengajar Ti Pelesu
3Menyadi, lebuh aku benung gagit ati nyendiaka diri nulis ngagai kita pasal pengelepas ti dikembuan semua kitai, aku ngira diri enda tau enda nulis ngagai kita minta kita bebendar gawa ke pengarap ti udah diberi sekali aja ngagai nembiak Tuhan. 4 Laban sekeda orang udah belalai enselitka diri tama ngagai bala kitai. Sida endang lama udah diletak deka diukum laban sida enda nangika Allah Taala. Sida nyarutka pesan pasal pengasih Allah Taala, lalu ngaga nya nyadika peluang kena sida ngereja pengawa ti kamah, lalu enggai ngaku Tuan enggau Tuhan kitai, Jesus Kristus, ti siku aja.
5 Diatu aku deka ngasuh kita ngingatka tu, taja pen kita udah nemu semua utai tu, iya nya, Tuhan udah ngelepaska orang Israel ari menua Ejip, tang udah nya, Iya munuh sida ke enda arap. 6Kingatka melikat ke enda nitihka sekat hak sida, tang ninggalka endur alai sida diau. Iya udah nanchang sida ngena rantai lalu nyimpan sida dalam endur ti pemadu petang, ngambika sida diakim lebuh Hari Pechara.
7 Lalu kingatka mega Sodom enggau Gomorah, enggau nengeri ti ngelingi nengeri dua buah nya, ti ngereja ulah ti kamah, lalu nyarutka pengawa beleman. Sida diukum ngena api ti enda nemu padam, kena ngajar semua mensia.

8Orang tu pen baka nya mega. Sida ngamahka tubuh diri, enggai diperintah Allah Taala, lalu mechat utai idup ti bemulia di serega.
        """
                )
            ),
            r"""
\v 1 Ari Jude, menyadi James, ke nyadi ulun Jesus Kristus,

Ngagai orang ke udah dikangau, ke dikerinduka Allah Taala ti Apai, sereta dijaga Jesus Kristus:

\v 2 Awakka pengasih, pemaik enggau pengerindu nambah-menambah diberi ngagai kita.
Pengajar Ti Pelesu
\v 3 Menyadi, lebuh aku benung gagit ati nyendiaka diri nulis ngagai kita pasal pengelepas ti dikembuan semua kitai, aku ngira diri enda tau enda nulis ngagai kita minta kita bebendar gawa ke pengarap ti udah diberi sekali aja ngagai nembiak Tuhan. \v 4 Laban sekeda orang udah belalai enselitka diri tama ngagai bala kitai. Sida endang lama udah diletak deka diukum laban sida enda nangika Allah Taala. Sida nyarutka pesan pasal pengasih Allah Taala, lalu ngaga nya nyadika peluang kena sida ngereja pengawa ti kamah, lalu enggai ngaku Tuan enggau Tuhan kitai, Jesus Kristus, ti siku aja.
\v 5 Diatu aku deka ngasuh kita ngingatka tu, taja pen kita udah nemu semua utai tu, iya nya, Tuhan udah ngelepaska orang Israel ari menua Ejip, tang udah nya, Iya munuh sida ke enda arap. \v 6 Kingatka melikat ke enda nitihka sekat hak sida, tang ninggalka endur alai sida diau. Iya udah nanchang sida ngena rantai lalu nyimpan sida dalam endur ti pemadu petang, ngambika sida diakim lebuh Hari Pechara.
\v 7 Lalu kingatka mega Sodom enggau Gomorah, enggau nengeri ti ngelingi nengeri dua buah nya, ti ngereja ulah ti kamah, lalu nyarutka pengawa beleman. Sida diukum ngena api ti enda nemu padam, kena ngajar semua mensia.

\v 8 Orang tu pen baka nya mega. Sida ngamahka tubuh diri, enggai diperintah Allah Taala, lalu mechat utai idup ti bemulia di serega.
        """,
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers17(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(
                fix_missing_space_after_number(
                    r"""
9 Indah tuai melikat ke benama Mikael deh enda berani mechat Sitan lebuh iya berebutka bangkai Moses enggau Sitan, tang semina nyebut, “Tuhan ngerara nuan!” 10Tang bala orang tu mechat semua utai ti enda ditemu sida reti. Lalu utai ti ditemu sida ngena pengasai, baka jelu ti enda nemu berunding, nya meh utai ti ngerusak sida. 11 Tulah meh sida! Sida niti jalai Kain, lalu ngereja penyalah ketegal duit baka penyalah ti dikereja Balaam, lalu sida dirusak baka Korah ke angkat ngelaban.
        """
                )
            ),
            r"""
\v 9 Indah tuai melikat ke benama Mikael deh enda berani mechat Sitan lebuh iya berebutka bangkai Moses enggau Sitan, tang semina nyebut, “Tuhan ngerara nuan!” \v 10 Tang bala orang tu mechat semua utai ti enda ditemu sida reti. Lalu utai ti ditemu sida ngena pengasai, baka jelu ti enda nemu berunding, nya meh utai ti ngerusak sida. \v 11 Tulah meh sida! Sida niti jalai Kain, lalu ngereja penyalah ketegal duit baka penyalah ti dikereja Balaam, lalu sida dirusak baka Korah ke angkat ngelaban.
        """,
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_usfm(self) -> None:
        lang_code = "iba-x-ibanempran"
        resource_type = "reg"
        book_code = "jud"
        self.assertEqual(
            fix_usfm(
                r"""
9 Indah tuai melikat ke benama Mikael deh enda berani mechat Sitan lebuh iya berebutka bangkai Moses enggau Sitan, tang semina nyebut, “Tuhan ngerara nuan!” 10Tang bala orang tu mechat semua utai ti enda ditemu sida reti. Lalu utai ti ditemu sida ngena pengasai, baka jelu ti enda nemu berunding, nya meh utai ti ngerusak sida. 11 Tulah meh sida! Sida niti jalai Kain, lalu ngereja penyalah ketegal duit baka penyalah ti dikereja Balaam, lalu sida dirusak baka Korah ke angkat ngelaban.
        """,
                lang_code,
                resource_type,
                book_code,
            ),
            r"""
\v 9 Indah tuai melikat ke benama Mikael deh enda berani mechat Sitan lebuh iya berebutka bangkai Moses enggau Sitan, tang semina nyebut, “Tuhan ngerara nuan!” \v 10 Tang bala orang tu mechat semua utai ti enda ditemu sida reti. Lalu utai ti ditemu sida ngena pengasai, baka jelu ti enda nemu berunding, nya meh utai ti ngerusak sida. \v 11 Tulah meh sida! Sida niti jalai Kain, lalu ngereja penyalah ketegal duit baka penyalah ti dikereja Balaam, lalu sida dirusak baka Korah ke angkat ngelaban.
        """,
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_after_number(self) -> None:
        self.assertEqual(
            fix_missing_space_after_number(r"\v 1Some text."),
            r"\v 1 Some text.",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_after_number2(self) -> None:
        self.assertEqual(
            fix_missing_space_after_number(r"\v 2Another verse."),
            r"\v 2 Another verse.",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_after_number3(self) -> None:
        self.assertEqual(
            fix_missing_space_after_number(r"\v 5 5Some text."),
            r"\v 5 5 Some text.",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_after_number4(self) -> None:
        self.assertEqual(
            # ("scg-x-mayau", "reg", "jas"),
            fix_missing_space_after_number(
                r"""\v 1  Jodi ntooh mo nya dik kaya,nongislah gook merataplah nih songsara dik nimpa mo? \v 2Kokaya mo jeh modamb,gok adohmo jeh oduk naiik gogat! \v 3  Omas ngant Perakmo jeh togoringk,togoringk,e dik jodi saksi tohadap mo gook akan ngudap daginggkmo wook opi,Mo jeh ngumpul rita pado onu-onu dik jeh pongkosiik.
"""
            ),
            r"""\v 1  Jodi ntooh mo nya dik kaya,nongislah gook merataplah nih songsara dik nimpa mo? \v 2 Kokaya mo jeh modamb,gok adohmo jeh oduk naiik gogat! \v 3  Omas ngant Perakmo jeh togoringk,togoringk,e dik jodi saksi tohadap mo gook akan ngudap daginggkmo wook opi,Mo jeh ngumpul rita pado onu-onu dik jeh pongkosiik.
""",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_after_number5(self) -> None:
        self.assertEqual(
            # ("iba-x-ibanempran", "reg", "jud"),
            fix_missing_space_after_number(
                r"""
24Ngagai Iya ke ulih nagang kita rebah, lalu nyerahka kita nadai bepenyalah sereta enggau ati ti gaga ngagai Iya ke bemulia, 25ngagai Allah Taala ti siku aja ke nyadi Juruselamat kitai, beri meh puji, mulia, pengering, enggau kuasa, ulih Jesus Kristus Tuhan kitai, kenyau ari dulu kelia, ngagai diatu, enggau ke belama-lama iya! Amin.
"""
            ),
            r"""
24 Ngagai Iya ke ulih nagang kita rebah, lalu nyerahka kita nadai bepenyalah sereta enggau ati ti gaga ngagai Iya ke bemulia, 25 ngagai Allah Taala ti siku aja ke nyadi Juruselamat kitai, beri meh puji, mulia, pengering, enggau kuasa, ulih Jesus Kristus Tuhan kitai, kenyau ari dulu kelia, ngagai diatu, enggau ke belama-lama iya! Amin.
""",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_missing_space_after_number6(self) -> None:
        self.assertEqual(
            fix_missing_space_after_number(
                r"""
9 Indah tuai melikat ke benama Mikael deh enda berani mechat Sitan lebuh iya berebutka bangkai Moses enggau Sitan, tang semina nyebut, “Tuhan ngerara nuan!” 10Tang bala orang tu mechat semua utai ti enda ditemu sida reti. Lalu utai ti ditemu sida ngena pengasai, baka jelu ti enda nemu berunding, nya meh utai ti ngerusak sida. 11 Tulah meh sida! Sida niti jalai Kain, lalu ngereja penyalah ketegal duit baka penyalah ti dikereja Balaam, lalu sida dirusak baka Korah ke angkat ngelaban.
        """
            ),
            r"""
9 Indah tuai melikat ke benama Mikael deh enda berani mechat Sitan lebuh iya berebutka bangkai Moses enggau Sitan, tang semina nyebut, “Tuhan ngerara nuan!” 10 Tang bala orang tu mechat semua utai ti enda ditemu sida reti. Lalu utai ti ditemu sida ngena pengasai, baka jelu ti enda nemu berunding, nya meh utai ti ngerusak sida. 11 Tulah meh sida! Sida niti jalai Kain, lalu ngereja penyalah ketegal duit baka penyalah ti dikereja Balaam, lalu sida dirusak baka Korah ke angkat ngelaban.
        """,
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_missing_space_after_number7(self) -> None:
        self.assertEqual(
            fix_missing_space_after_number(
                r"""
\v 1 Indro tahaky gny ino gny fitiava nomen'gny Ray asika,ba hitokava asika ho Zanak'Agnahary, dra zay isika. Noho zay atony zay, zao totolo zao dra sy mahafatsy asika, satria sy mahafatasy anazy zay. [ Fanamariha : gny dika-zaka taloha dra sy magnisy ho:''Dra izay isika.''] \v 2 Ry malala, zanak'Agnahary isika amizao, dra zay dra bo sy nambara ho hanahaky gny ino isika . Isika dra mahafatasy fa gny miseho i Kristy,dra ho tahaky Anazy isika, satria hahita Anazy manahaky Anazy isika. \v 3 Gny ze mana anizay fahatokisa momba gny ho avy mifotosy aminazy zay dra magnalio gny vatany ba halio tahaky Anazy.
\v 4 Zay manota iaby dra manao ze sy ara-dalana; fa gny fahota dra sy ara-dalana. \v 5 Andrareo dra mahafatasy fa i Kristy dra nambara ba hangalaky reo fahota, dra ao aminazy dra sy misy fahota. \v 6 Sy misy olo ze mitoesy ao aminazy dra bo manota nahita anazy dre nahafatasy anazy.
\v 7 Ry zanaky malala, ka anga hisy olo hamitaky andrareo, gny raiky ze manao gny fahamarigna dra mary,tahaky gny mahamarigna an'i Kristy. \v 8 Gny raiky ze manota dra laha tamin'gny devoly,fa gny devoly dra nanota hatragny am-bolohany. Noho zay atony zay gny Zanak'Agnahary dra naseho, ba hahafahany mandrava reo asan'gny devoly.
\v 9 Dre iza dre iza naterak'Agnahary dra sy hanohy gny fahota satria gny tegnany laha tamin'Agnahary dra mitoesy ao aminazy. Sy afaky manohy gny fahota izy satria naterak 'Agnahary. \v 10 Ao amin'izay gny hampiboahany reo zanak'Agnahary vo reo zanaky gny devoly. Dre iza dre iza sy manao gny mary dra sy laha tamin'Agnahary; dre gny raiky ze sy tia gny rahalahiny avo koa .
\v 11 Fa zay gny hafasy ze fa rendrareo hatragny am-piboahany: fa isika dra tokony mifakatia, \v 12 fa sy manahaky an'i Kaina, ze laha tamin'gny rasy vo namono gny rahalahiny. Fa nanao akory izy gny namono anazy? Satria reo asany dra rasy , dra gny agny rahalahiny dra mary.
\v 13 Ka gaga,ry rahalahiko,raha malaiky andrareo gny tany. \v 14 Fatasika fa niala tamin'gny fahafatesa magnagny ami fiaigna isika satria tia an'ereo rahalahiny isika. Zay sy tia dra mitoesy agny amy fahafatesa. \v 15 Ze malaiky gny rahalahiny dra mpamono olo. Fatasindrareo fa sy misy mpamono olo mana fiaigna mandrakizay mitoesy ao aminazy.
\v 16 Amin'izay gny hahafatarasika gny fitiava, satria Kristy nanolosy gny ainy hi asika. Isika avo koa dra tokony manolosy gny aisika ho an'ireo rahalahy.\v 17 Fa dre iza dre iza mana gny hanagnan'izao totolo zao zao, dra mahita gny fahasahiragnan'gny rahalahiny, dra mandrindry gny fony fangorahany anazy, amin'gny fomba manao akory gny hipetraran'gny fitiavan'Agnahary ao aminazy? \v 18 Ry zanako malalako, ao isika sy hitia amin'gny zaka dre koa amy vava, fa amin'gny asa vo fahamarigna.
\v 19 Avy amin'izay gny hahafatarasika fa avy amin'gny fahamarina isika, dra mampatoky gny fosika eo anatrehany isika. \v 20 Fa raha magnahy asika gny fosika, Zagnahary dra lahibe noho gny fosika,dra mahafatasy gny raha-iaby Izy. \v 21 Ry malala, raha sy magnahy asika gny fosika, dra mana fahatokisa amin'Agnahary isika. \v 22 Dre ino dre ino angatahisika dra ho azosika laha taminazy, satria isika mitandry reo didiny vo manao ze tiany eo anatrehany.
\v 23 Zao gny didiny: tokony mino gny agnaran'gny Zanany Jesosy Kristy dra mifakatia isika, tahaky gny fa nagnomezany asika ze didy zay. \v 24 Gny raiky ze mita reo didin'Agnahary dra mitoesy ao aminazy, dra Zagnahary mitoesy ao aminazy. Amin'izay gny hahafatarasika fa izy dra mitoera ao amisika, amin'gny Fagnahy ze nomeny asika.
        """
            ),
            r"""
\v 1 Indro tahaky gny ino gny fitiava nomen'gny Ray asika,ba hitokava asika ho Zanak'Agnahary, dra zay isika. Noho zay atony zay, zao totolo zao dra sy mahafatsy asika, satria sy mahafatasy anazy zay. [ Fanamariha : gny dika-zaka taloha dra sy magnisy ho:''Dra izay isika.''] \v 2 Ry malala, zanak'Agnahary isika amizao, dra zay dra bo sy nambara ho hanahaky gny ino isika . Isika dra mahafatasy fa gny miseho i Kristy,dra ho tahaky Anazy isika, satria hahita Anazy manahaky Anazy isika. \v 3 Gny ze mana anizay fahatokisa momba gny ho avy mifotosy aminazy zay dra magnalio gny vatany ba halio tahaky Anazy.
\v 4 Zay manota iaby dra manao ze sy ara-dalana; fa gny fahota dra sy ara-dalana. \v 5 Andrareo dra mahafatasy fa i Kristy dra nambara ba hangalaky reo fahota, dra ao aminazy dra sy misy fahota. \v 6 Sy misy olo ze mitoesy ao aminazy dra bo manota nahita anazy dre nahafatasy anazy.
\v 7 Ry zanaky malala, ka anga hisy olo hamitaky andrareo, gny raiky ze manao gny fahamarigna dra mary,tahaky gny mahamarigna an'i Kristy. \v 8 Gny raiky ze manota dra laha tamin'gny devoly,fa gny devoly dra nanota hatragny am-bolohany. Noho zay atony zay gny Zanak'Agnahary dra naseho, ba hahafahany mandrava reo asan'gny devoly.
\v 9 Dre iza dre iza naterak'Agnahary dra sy hanohy gny fahota satria gny tegnany laha tamin'Agnahary dra mitoesy ao aminazy. Sy afaky manohy gny fahota izy satria naterak 'Agnahary. \v 10 Ao amin'izay gny hampiboahany reo zanak'Agnahary vo reo zanaky gny devoly. Dre iza dre iza sy manao gny mary dra sy laha tamin'Agnahary; dre gny raiky ze sy tia gny rahalahiny avo koa .
\v 11 Fa zay gny hafasy ze fa rendrareo hatragny am-piboahany: fa isika dra tokony mifakatia, \v 12 fa sy manahaky an'i Kaina, ze laha tamin'gny rasy vo namono gny rahalahiny. Fa nanao akory izy gny namono anazy? Satria reo asany dra rasy , dra gny agny rahalahiny dra mary.
\v 13 Ka gaga,ry rahalahiko,raha malaiky andrareo gny tany. \v 14 Fatasika fa niala tamin'gny fahafatesa magnagny ami fiaigna isika satria tia an'ereo rahalahiny isika. Zay sy tia dra mitoesy agny amy fahafatesa. \v 15 Ze malaiky gny rahalahiny dra mpamono olo. Fatasindrareo fa sy misy mpamono olo mana fiaigna mandrakizay mitoesy ao aminazy.
\v 16 Amin'izay gny hahafatarasika gny fitiava, satria Kristy nanolosy gny ainy hi asika. Isika avo koa dra tokony manolosy gny aisika ho an'ireo rahalahy.\v 17 Fa dre iza dre iza mana gny hanagnan'izao totolo zao zao, dra mahita gny fahasahiragnan'gny rahalahiny, dra mandrindry gny fony fangorahany anazy, amin'gny fomba manao akory gny hipetraran'gny fitiavan'Agnahary ao aminazy? \v 18 Ry zanako malalako, ao isika sy hitia amin'gny zaka dre koa amy vava, fa amin'gny asa vo fahamarigna.
\v 19 Avy amin'izay gny hahafatarasika fa avy amin'gny fahamarina isika, dra mampatoky gny fosika eo anatrehany isika. \v 20 Fa raha magnahy asika gny fosika, Zagnahary dra lahibe noho gny fosika,dra mahafatasy gny raha-iaby Izy. \v 21 Ry malala, raha sy magnahy asika gny fosika, dra mana fahatokisa amin'Agnahary isika. \v 22 Dre ino dre ino angatahisika dra ho azosika laha taminazy, satria isika mitandry reo didiny vo manao ze tiany eo anatrehany.
\v 23 Zao gny didiny: tokony mino gny agnaran'gny Zanany Jesosy Kristy dra mifakatia isika, tahaky gny fa nagnomezany asika ze didy zay. \v 24 Gny raiky ze mita reo didin'Agnahary dra mitoesy ao aminazy, dra Zagnahary mitoesy ao aminazy. Amin'izay gny hahafatarasika fa izy dra mitoera ao amisika, amin'gny Fagnahy ze nomeny asika.
        """,
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_before_number(self) -> None:
        self.assertEqual(
            fix_missing_space_before_number(r"Wut.1 Some text."),
            r"Wut. 1 Some text.",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_before_number2(self) -> None:
        self.assertEqual(
            fix_missing_space_before_number(r"Wut.1 Some text. \v 2 Yo"),
            r"Wut. 1 Some text. \v 2 Yo",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_before_number3(self) -> None:
        self.assertEqual(
            fix_missing_space_before_number(
                r"""
1Laban aku dekaka kita nemu pemendar aku bekereja ke kita, enggau ke sida ke di Laudisia, enggau ke semua orang ke enda kala betemu betunga mua enggau aku. 2Aku dekaka ati sida diperansang sereta begempung dalam pengerindu, ngambika sida meretika semua utai, lalu nemu misteri Allah Taala, iya nya Kristus Empu,3 ke alai semua penemu-dalam enggau penemu dilalaika.
                """
            ),
            r"""
1Laban aku dekaka kita nemu pemendar aku bekereja ke kita, enggau ke sida ke di Laudisia, enggau ke semua orang ke enda kala betemu betunga mua enggau aku. 2Aku dekaka ati sida diperansang sereta begempung dalam pengerindu, ngambika sida meretika semua utai, lalu nemu misteri Allah Taala, iya nya Kristus Empu, 3 ke alai semua penemu-dalam enggau penemu dilalaika.
                """,
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_before_number4(self) -> None:
        actual = fix_missing_space_before_number(
            r"""
\v 1 ذيه نسب عيسى المسيح ابن داود ابن ابراهيم \b \li1 \v 2 ابراهيم ولد اسحاق \li1 واسحاق ولد يعقوب \li1 ويعقوب ولد يهوذا واخوته \li1 \v 3 ويهوذا ولد فارص وزارح من ثامار \li1 وفارص ولد حصرون \li1 وحصرو ولد ارام \li1
"""
        )
        expected = r"""
\v 1 ذيه نسب عيسى المسيح ابن داود ابن ابراهيم \b \li1 \v 2 ابراهيم ولد اسحاق \li1 واسحاق ولد يعقوب \li1 ويعقوب ولد يهوذا واخوته \li1 \v 3 ويهوذا ولد فارص وزارح من ثامار \li1 وفارص ولد حصرون \li1 وحصرو ولد ارام \li1
"""
        print("Expected: ", expected)
        print("Actual:   ", actual)
        self.assertEqual(actual, expected)

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_before_number5(self) -> None:
        self.assertEqual(
            fix_missing_space_before_number(
                r"""
\v 1 ذيه نسب عيسى المسيح ابن داود ابن ابراهيم \b \q1 \v 2 ابراهيم ولد اسحاق \li1 واسحاق ولد يعقوب \li1 ويعقوب ولد يهوذا واخوته \li1 \v 3 ويهوذا ولد فارص وزارح من ثامار \li1 وفارص ولد حصرون \li1 وحصرو ولد ارام \li1
"""
            ),
            r"""
\v 1 ذيه نسب عيسى المسيح ابن داود ابن ابراهيم \b \q1 \v 2 ابراهيم ولد اسحاق \li1 واسحاق ولد يعقوب \li1 ويعقوب ولد يهوذا واخوته \li1 \v 3 ويهوذا ولد فارص وزارح من ثامار \li1 وفارص ولد حصرون \li1 وحصرو ولد ارام \li1
""",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_before_number6(self) -> None:
        actual = fix_missing_space_before_number(
            r"""
\v 8 وفلتين النسوان القبر سريع وهن خايفات وفارحات قوي ، وكانين يجرين علميد يبشرين الطلاب \v 9 فلقيهن عيسى في الطريق وقال لهن :(السلام عليكما) وقربين منه ومسكين ارجله وسجدين له \v 10 فقال لهن عيسى :(لا تخافينش ، سيرين لإخوتي وقولين لهم انهم يسيروا للجليل ، وهاناك عيبسروني)
"""
        )
        expected = r"""
\v 8 وفلتين النسوان القبر سريع وهن خايفات وفارحات قوي ، وكانين يجرين علميد يبشرين الطلاب \v 9 فلقيهن عيسى في الطريق وقال لهن :(السلام عليكما) وقربين منه ومسكين ارجله وسجدين له \v 10 فقال لهن عيسى :(لا تخافينش ، سيرين لإخوتي وقولين لهم انهم يسيروا للجليل ، وهاناك عيبسروني)
"""
        print("Expected: ", expected)
        print("Actual:   ", actual)
        self.assertEqual(actual, expected)

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_before_verse_marker(self) -> None:
        self.assertEqual(
            fix_missing_space_before_verse_marker(r"Wut\v 1Some text."),
            r"Wut \v 1Some text.",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_before_verse_marker2(self) -> None:
        self.assertEqual(
            fix_missing_space_before_verse_marker(
                r"\v 2Another verse.\v 3 This is more text."
            ),
            r"\v 2Another verse. \v 3 This is more text.",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_before_verse_marker3(self) -> None:
        self.assertEqual(
            fix_missing_space_before_verse_marker(r"\v 5 5Some text."),
            r"\v 5 5Some text.",
        )

    # @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_before_verse_marker4(self) -> None:
        self.assertEqual(
            fix_missing_space_before_verse_marker(
                r"""
\v 1 Indro tahaky gny ino gny fitiava nomen'gny Ray asika,ba hitokava asika ho Zanak'Agnahary, dra zay isika. Noho zay atony zay, zao totolo zao dra sy mahafatsy asika, satria sy mahafatasy anazy zay. [ Fanamariha : gny dika-zaka taloha dra sy magnisy ho:''Dra izay isika.''] \v 2 Ry malala, zanak'Agnahary isika amizao, dra zay dra bo sy nambara ho hanahaky gny ino isika . Isika dra mahafatasy fa gny miseho i Kristy,dra ho tahaky Anazy isika, satria hahita Anazy manahaky Anazy isika. \v 3 Gny ze mana anizay fahatokisa momba gny ho avy mifotosy aminazy zay dra magnalio gny vatany ba halio tahaky Anazy.
\v 4 Zay manota iaby dra manao ze sy ara-dalana; fa gny fahota dra sy ara-dalana. \v 5 Andrareo dra mahafatasy fa i Kristy dra nambara ba hangalaky reo fahota, dra ao aminazy dra sy misy fahota. \v 6 Sy misy olo ze mitoesy ao aminazy dra bo manota nahita anazy dre nahafatasy anazy.
\v 7 Ry zanaky malala, ka anga hisy olo hamitaky andrareo, gny raiky ze manao gny fahamarigna dra mary,tahaky gny mahamarigna an'i Kristy. \v 8 Gny raiky ze manota dra laha tamin'gny devoly,fa gny devoly dra nanota hatragny am-bolohany. Noho zay atony zay gny Zanak'Agnahary dra naseho, ba hahafahany mandrava reo asan'gny devoly.
\v 9 Dre iza dre iza naterak'Agnahary dra sy hanohy gny fahota satria gny tegnany laha tamin'Agnahary dra mitoesy ao aminazy. Sy afaky manohy gny fahota izy satria naterak 'Agnahary. \v 10 Ao amin'izay gny hampiboahany reo zanak'Agnahary vo reo zanaky gny devoly. Dre iza dre iza sy manao gny mary dra sy laha tamin'Agnahary; dre gny raiky ze sy tia gny rahalahiny avo koa .
\v 11 Fa zay gny hafasy ze fa rendrareo hatragny am-piboahany: fa isika dra tokony mifakatia, \v 12 fa sy manahaky an'i Kaina, ze laha tamin'gny rasy vo namono gny rahalahiny. Fa nanao akory izy gny namono anazy? Satria reo asany dra rasy , dra gny agny rahalahiny dra mary.
\v 13 Ka gaga,ry rahalahiko,raha malaiky andrareo gny tany. \v 14 Fatasika fa niala tamin'gny fahafatesa magnagny ami fiaigna isika satria tia an'ereo rahalahiny isika. Zay sy tia dra mitoesy agny amy fahafatesa. \v 15 Ze malaiky gny rahalahiny dra mpamono olo. Fatasindrareo fa sy misy mpamono olo mana fiaigna mandrakizay mitoesy ao aminazy.
\v 16 Amin'izay gny hahafatarasika gny fitiava, satria Kristy nanolosy gny ainy hi asika. Isika avo koa dra tokony manolosy gny aisika ho an'ireo rahalahy.\v 17 Fa dre iza dre iza mana gny hanagnan'izao totolo zao zao, dra mahita gny fahasahiragnan'gny rahalahiny, dra mandrindry gny fony fangorahany anazy, amin'gny fomba manao akory gny hipetraran'gny fitiavan'Agnahary ao aminazy? \v 18 Ry zanako malalako, ao isika sy hitia amin'gny zaka dre koa amy vava, fa amin'gny asa vo fahamarigna.
\v 19 Avy amin'izay gny hahafatarasika fa avy amin'gny fahamarina isika, dra mampatoky gny fosika eo anatrehany isika. \v 20 Fa raha magnahy asika gny fosika, Zagnahary dra lahibe noho gny fosika,dra mahafatasy gny raha-iaby Izy. \v 21 Ry malala, raha sy magnahy asika gny fosika, dra mana fahatokisa amin'Agnahary isika. \v 22 Dre ino dre ino angatahisika dra ho azosika laha taminazy, satria isika mitandry reo didiny vo manao ze tiany eo anatrehany.
\v 23 Zao gny didiny: tokony mino gny agnaran'gny Zanany Jesosy Kristy dra mifakatia isika, tahaky gny fa nagnomezany asika ze didy zay. \v 24 Gny raiky ze mita reo didin'Agnahary dra mitoesy ao aminazy, dra Zagnahary mitoesy ao aminazy. Amin'izay gny hahafatarasika fa izy dra mitoera ao amisika, amin'gny Fagnahy ze nomeny asika.
        """
            ),
            r"""
\v 1 Indro tahaky gny ino gny fitiava nomen'gny Ray asika,ba hitokava asika ho Zanak'Agnahary, dra zay isika. Noho zay atony zay, zao totolo zao dra sy mahafatsy asika, satria sy mahafatasy anazy zay. [ Fanamariha : gny dika-zaka taloha dra sy magnisy ho:''Dra izay isika.''] \v 2 Ry malala, zanak'Agnahary isika amizao, dra zay dra bo sy nambara ho hanahaky gny ino isika . Isika dra mahafatasy fa gny miseho i Kristy,dra ho tahaky Anazy isika, satria hahita Anazy manahaky Anazy isika. \v 3 Gny ze mana anizay fahatokisa momba gny ho avy mifotosy aminazy zay dra magnalio gny vatany ba halio tahaky Anazy.
\v 4 Zay manota iaby dra manao ze sy ara-dalana; fa gny fahota dra sy ara-dalana. \v 5 Andrareo dra mahafatasy fa i Kristy dra nambara ba hangalaky reo fahota, dra ao aminazy dra sy misy fahota. \v 6 Sy misy olo ze mitoesy ao aminazy dra bo manota nahita anazy dre nahafatasy anazy.
\v 7 Ry zanaky malala, ka anga hisy olo hamitaky andrareo, gny raiky ze manao gny fahamarigna dra mary,tahaky gny mahamarigna an'i Kristy. \v 8 Gny raiky ze manota dra laha tamin'gny devoly,fa gny devoly dra nanota hatragny am-bolohany. Noho zay atony zay gny Zanak'Agnahary dra naseho, ba hahafahany mandrava reo asan'gny devoly.
\v 9 Dre iza dre iza naterak'Agnahary dra sy hanohy gny fahota satria gny tegnany laha tamin'Agnahary dra mitoesy ao aminazy. Sy afaky manohy gny fahota izy satria naterak 'Agnahary. \v 10 Ao amin'izay gny hampiboahany reo zanak'Agnahary vo reo zanaky gny devoly. Dre iza dre iza sy manao gny mary dra sy laha tamin'Agnahary; dre gny raiky ze sy tia gny rahalahiny avo koa .
\v 11 Fa zay gny hafasy ze fa rendrareo hatragny am-piboahany: fa isika dra tokony mifakatia, \v 12 fa sy manahaky an'i Kaina, ze laha tamin'gny rasy vo namono gny rahalahiny. Fa nanao akory izy gny namono anazy? Satria reo asany dra rasy , dra gny agny rahalahiny dra mary.
\v 13 Ka gaga,ry rahalahiko,raha malaiky andrareo gny tany. \v 14 Fatasika fa niala tamin'gny fahafatesa magnagny ami fiaigna isika satria tia an'ereo rahalahiny isika. Zay sy tia dra mitoesy agny amy fahafatesa. \v 15 Ze malaiky gny rahalahiny dra mpamono olo. Fatasindrareo fa sy misy mpamono olo mana fiaigna mandrakizay mitoesy ao aminazy.
\v 16 Amin'izay gny hahafatarasika gny fitiava, satria Kristy nanolosy gny ainy hi asika. Isika avo koa dra tokony manolosy gny aisika ho an'ireo rahalahy. \v 17 Fa dre iza dre iza mana gny hanagnan'izao totolo zao zao, dra mahita gny fahasahiragnan'gny rahalahiny, dra mandrindry gny fony fangorahany anazy, amin'gny fomba manao akory gny hipetraran'gny fitiavan'Agnahary ao aminazy? \v 18 Ry zanako malalako, ao isika sy hitia amin'gny zaka dre koa amy vava, fa amin'gny asa vo fahamarigna.
\v 19 Avy amin'izay gny hahafatarasika fa avy amin'gny fahamarina isika, dra mampatoky gny fosika eo anatrehany isika. \v 20 Fa raha magnahy asika gny fosika, Zagnahary dra lahibe noho gny fosika,dra mahafatasy gny raha-iaby Izy. \v 21 Ry malala, raha sy magnahy asika gny fosika, dra mana fahatokisa amin'Agnahary isika. \v 22 Dre ino dre ino angatahisika dra ho azosika laha taminazy, satria isika mitandry reo didiny vo manao ze tiany eo anatrehany.
\v 23 Zao gny didiny: tokony mino gny agnaran'gny Zanany Jesosy Kristy dra mifakatia isika, tahaky gny fa nagnomezany asika ze didy zay. \v 24 Gny raiky ze mita reo didin'Agnahary dra mitoesy ao aminazy, dra Zagnahary mitoesy ao aminazy. Amin'izay gny hahafatarasika fa izy dra mitoera ao amisika, amin'gny Fagnahy ze nomeny asika.
        """,
        )

    @pytest.mark.usfm_fixes
    def test_fix_space_after_section_marker(self) -> None:
        self.assertEqual(
            fix_space_after_section_marker(r"\s 1 Some text."),
            r"\s1 Some text.",
        )
        self.assertEqual(
            fix_space_after_section_marker(r"\s 2Another verse."),
            r"\s2Another verse.",
        )
        self.assertEqual(
            fix_space_after_section_marker(r"\s 5 5Some text."),
            r"\s5 5Some text.",
        )

    @pytest.mark.usfm_fixes
    def test_replace_cc_with_c(self) -> None:
        self.assertEqual(
            replace_cc_with_c(
                r"""
\c 1
\c 1
Some text.
"""
            ),
            r"""
\c 1
Some text.
""",
        )
        self.assertEqual(
            replace_cc_with_c(
                r"""
\c 14
\c 14
\p
\v 1 Sansonso' Tinatoquë pa'marin. Inaquë nicapon pochin a'na sanapi, quënanin. Inaso a'na Huiristia quëmapi, hui'nin. \v 2 Ina quëran Sansonso' huëantarin. Pa'pin ashin inapita, sha'huitërin:"Tinato ninanoquë Huiristia sanapi, quënanahuë. Paatoma anoyatoco maca'huaso marë'," itërin.
"""
            ),
            r"""
\c 14
\p
\v 1 Sansonso' Tinatoquë pa'marin. Inaquë nicapon pochin a'na sanapi, quënanin. Inaso a'na Huiristia quëmapi, hui'nin. \v 2 Ina quëran Sansonso' huëantarin. Pa'pin ashin inapita, sha'huitërin:"Tinato ninanoquë Huiristia sanapi, quënanahuë. Paatoma anoyatoco maca'huaso marë'," itërin.
""",
        )

    @pytest.mark.usfm_fixes
    def test_replace_n_with_v(self) -> None:
        self.assertEqual(
            replace_n_with_v(r"""\n 1 This is some text \n 2 Some other text"""),
            r"""\v 1 This is some text \v 2 Some other text""",
        )


if __name__ == "__main__":
    unittest.main()
