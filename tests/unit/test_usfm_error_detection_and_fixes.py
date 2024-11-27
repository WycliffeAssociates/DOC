import pytest
import unittest
from document.domain.usfm_error_detection_and_fixes import (
    remove_null_bytes_and_control_characters,
    fix_dot_after_verse_number,
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

    @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(r"1 Some text."),
            r"\v 1 Some text.",
        )

    @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers2(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(r"1 Some text. 2 This is more text."),
            r"\v 1 Some text. \v 2 This is more text.",
        )

    @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers3(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(r"\v 1 Some text. \v 2 This is more text."),
            r"\v 1 Some text. \v 2 This is more text.",
        )

    @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers4(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(r"1 Some text. \v 2 This is more text."),
            r"\v 1 Some text. \v 2 This is more text.",
        )

    @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers5(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(r"\c 1 Some text. \v 1 This is more text."),
            r"\c 1 Some text. \v 1 This is more text.",
        )

    @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers6(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(r"\1 Some text. \2 This is more text."),
            r"\1 Some text. \2 This is more text.",
        )

    @pytest.mark.focus
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

    @pytest.mark.focus
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

    @pytest.mark.focus
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

    @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers10(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(
                r"""\v 15 وأليود ولد أليعازر \li1 وأليعازر ولد متان \li1 ومتان ولد يعقوب \li1 \v 16 ويعقوب ولد يوسف رجل مريم اللي ولدت عيسى اللي يسموه المسيح \li4 \v 17 ويطلع مجموع الأجيال من إبراهيم إلى داود 14 جيل ومن داود إلى الأسر البابلي 14 جيل ومن الأسر البابلي إلى المسيح 14 جيل"""
            ),
            r"""\v 15 وأليود ولد أليعازر \li1 وأليعازر ولد متان \li1 ومتان ولد يعقوب \li1 \v 16 ويعقوب ولد يوسف رجل مريم اللي ولدت عيسى اللي يسموه المسيح \li4 \v 17 ويطلع مجموع الأجيال من إبراهيم إلى داود 14 جيل ومن داود إلى الأسر البابلي 14 جيل ومن الأسر البابلي إلى المسيح 14 جيل""",
        )

    @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers11(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(
                r"""\v 1 This is a verse \v2 this is another verse 3 and this verse too 4 and another as well"""
            ),
            r"""\v 1 This is a verse \v2 this is another verse \v 3 and this verse too \v 4 and another as well""",
        )

    @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_standalone_verse_numbers12(self) -> None:
        self.assertEqual(
            fix_standalone_verse_numbers(
                r"""\v 1 This is a verse \v2 this is another verse 3 and this verse too 3 and another as well"""
            ),
            r"""\v 1 This is a verse \v2 this is another verse 3 and this verse too 3 and another as well""",
        )

    @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_after_number(self) -> None:
        self.assertEqual(
            fix_missing_space_after_number(r"\v 1Some text."),
            r"\v 1 Some text.",
        )

    @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_after_number2(self) -> None:
        self.assertEqual(
            fix_missing_space_after_number(r"\v 2Another verse."),
            r"\v 2 Another verse.",
        )

    @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_after_number3(self) -> None:
        self.assertEqual(
            fix_missing_space_after_number(r"\v 5 5Some text."),
            r"\v 5 5 Some text.",
        )

    @pytest.mark.focus
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

    @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_before_number(self) -> None:
        self.assertEqual(
            fix_missing_space_before_number(r"Wut.1 Some text."),
            r"Wut. 1 Some text.",
        )

    @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_before_number2(self) -> None:
        self.assertEqual(
            fix_missing_space_before_number(r"Wut.1 Some text. \v 2 Yo"),
            r"Wut. 1 Some text. \v 2 Yo",
        )

    @pytest.mark.focus
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

    @pytest.mark.focus
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

    @pytest.mark.focus
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

    @pytest.mark.focus
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

    @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_before_verse_marker(self) -> None:
        self.assertEqual(
            fix_missing_space_before_verse_marker(r"Wut\v 1Some text."),
            r"Wut \v 1Some text.",
        )

    @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_before_verse_marker2(self) -> None:
        self.assertEqual(
            fix_missing_space_before_verse_marker(
                r"\v 2Another verse.\v 3 This is more text."
            ),
            r"\v 2Another verse. \v 3 This is more text.",
        )

    @pytest.mark.focus
    @pytest.mark.usfm_fixes
    def test_fix_missing_space_before_verse_marker3(self) -> None:
        self.assertEqual(
            fix_missing_space_before_verse_marker(r"\v 5 5Some text."),
            r"\v 5 5Some text.",
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
