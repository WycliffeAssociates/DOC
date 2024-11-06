import pytest
import unittest
from document.domain.usfm_error_detection_and_fixes import (
    remove_null_bytes_and_control_characters,
    fix_dot_after_verse_number,
    fix_verse_marker_without_v,
    fix_missing_space_after_verse_number,
    replace_n_with_v,
)


class USFMErrorDetection(unittest.TestCase):
    maxDiff = None

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
                remove_null_bytes_and_control_characters(
                    r"\v 1. Ba yuku wekam tala ba na,ah i yanzangulah, yuka bi yidi wei ɓalang , ban i ninsim yau, ii yau kala ii nin a lanɓa. \v 2 . Wei balang ka wei Nyiibilah ba tahfahza ibi lah ding. \v 3 . Kacho sacha i ninvii i saetam tafahza ɓafuh tah gabi ii bah Yeeso Krisi kala wii tahgabi wei balang i bah yidibe."
                )
            ),
            r"\v 1 Ba yuku wekam tala ba na,ah i yanzangulah, yuka bi yidi wei ɓalang , ban i ninsim yau, ii yau kala ii nin a lanɓa. \v 2 Wei balang ka wei Nyiibilah ba tahfahza ibi lah ding. \v 3 Kacho sacha i ninvii i saetam tafahza ɓafuh tah gabi ii bah Yeeso Krisi kala wii tahgabi wei balang i bah yidibe.",
        )

    @pytest.mark.focus
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
                remove_null_bytes_and_control_characters(
                    # gwg php
                    r""""\c 1\cl Chapter 1
\1.Bulus I Timoti zab I ya nwohlo Yeso,wala be yauka ii Raman loi we Almasihu Yeso kai Filibi la ɓa ,I yauka la na ɓi wekhem ii ya ɗinkin la.\2.Na ni nha Malang ah I ɓa lah i satem ba fuh tahgaɓi ya Yeso Almasihu la.
\3. Vinse na man kpha fuhm ka nan zii bagaba.\4.Vinse we ba linwabung ɓuocnham la,la bagaba se ,Ii nyin faram la Neman li nwah buock.\5.Na man kha fuh la bai ba gamza gabq we bai fuh la bepiu la wulah vii a jekang.\6.In bi yang la bai ninka,Yuka be pi ba ba chonin ala we ba la ba ,au tarta vii kau u gama wala vii ba wai Yeso Almasihu."""
                )
            ),
            r""""\c 1\cl Chapter 1\v 1 Bulus I Timoti zab I ya nwohlo Yeso,wala be yauka ii Raman loi we Almasihu Yeso kai Filibi la ɓa ,I yauka la na ɓi wekhem ii ya ɗinkin la.\v 2 Na ni nha Malang ah I ɓa lah i satem ba fuh tahgaɓi ya Yeso Almasihu la.\v 3 Vinse na man kpha fuhm ka nan zii bagaba.\v 4 Vinse we ba linwabung ɓuocnham la,la bagaba se ,Ii nyin faram la Neman li nwah buock.\v 5 Na man kha fuh la bai ba gamza gabq we bai fuh la bepiu la wulah vii a jekang.\v 6 In bi yang la bai ninka,Yuka be pi ba ba chonin ala we ba la ba ,au tarta vii kau u gama wala vii ba wai Yeso Almasihu.""",
        )

    def test_fix_missing_space_after_verse_number(self) -> None:
        self.assertEqual(
            fix_missing_space_after_verse_number(r"\v 1Some text."),
            r"\v 1 Some text.",
        )
        self.assertEqual(
            fix_missing_space_after_verse_number(r"\v 2Another verse."),
            r"\v 2 Another verse.",
        )
        self.assertEqual(
            fix_missing_space_after_verse_number(r"\v 5 5Some text."),
            r"\v 5 5Some text.",
        )
        self.assertEqual(
            # ("scg-x-mayau", "reg", "jas"),
            fix_missing_space_after_verse_number(
                remove_null_bytes_and_control_characters(
                    r"""\v 1  Jodi ntooh mo nya dik kaya,nongislah gook merataplah nih songsara dik nimpa mo? \v 2 Kokaya mo jeh modamb,gok adohmo jeh oduk naiik gogat! \v 3  Omas ngant Perakmo jeh togoringk,togoringk,e dik jodi saksi tohadap mo gook akan ngudap daginggkmo wook opi,Mo jeh ngumpul rita pado onu-onu dik jeh pongkosiik.

\v 4.Sosunguh bah jeh tokapingk pangkoos daiik,korina nih upah dik nih mo nahant sik kuli diik jeh ngkodi miih nyak mo,ngant jeh sampae koni kopingk Ponompa sidiik bonua poya tona posungunt nya dik ngotimmp miih mo.\v 5 Waah komiwahmo jeh libo midoop ngant gook bofoya-foya wah Bumi,Mo jeh mpuas owangkkmo libo onu nya mollehh,\v 6 Mo jeh ngukumpp bahkan ngkomis ntoyant dik bonar ngant domp kae dopat nlawonnt mo.
\v 7.Nih nyent,Yah dorumak bosabar maeeh sampai pongkonik Ponompa! Sosunguh Poruma nungukk asel dik boroga siik poya,e ngant domp sabarr sampae jeh tomonah onu ujannt,onu gugorr ngant onu semi.\v 8 Mo geeh arus bosabar ngant arus nogarr owangk mo,Korina pongkonik Ponompa jeh Monikk.
"""
                )
            ),
            r"""\v 1  Jodi ntooh mo nya dik kaya,nongislah gook merataplah nih songsara dik nimpa mo? \v 2 Kokaya mo jeh modamb,gok adohmo jeh oduk naiik gogat! \v 3  Omas ngant Perakmo jeh togoringk,togoringk,e dik jodi saksi tohadap mo gook akan ngudap daginggkmo wook opi,Mo jeh ngumpul rita pado onu-onu dik jeh pongkosiik. \v 4 Sosunguh bah jeh tokapingk pangkoos daiik,korina nih upah dik nih mo nahant sik kuli diik jeh ngkodi miih nyak mo,ngant jeh sampae koni kopingk Ponompa sidiik bonua poya tona posungunt nya dik ngotimmp miih mo. \v 5 Waah komiwahmo jeh libo midoop ngant gook bofoya-foya wah Bumi,Mo jeh mpuas owangkkmo libo onu nya mollehh, \v 6 Mo jeh ngukumpp bahkan ngkomis ntoyant dik bonar ngant domp kae dopat nlawonnt mo. \v 7 Nih nyent,Yah dorumak bosabar maeeh sampai pongkonik Ponompa! Sosunguh Poruma nungukk asel dik boroga siik poya,e ngant domp sabarr sampae jeh tomonah onu ujannt,onu gugorr ngant onu semi. \v 8 Mo geeh arus bosabar ngant arus nogarr owangk mo,Korina pongkonik Ponompa jeh Monikk.
""",
        )

    def test_replace_n_with_v(self) -> None:
        self.assertEqual(
            replace_n_with_v(r"\n 1 This is some text \n 2 Some other text"),
            r"\v 1 This is some text \v 2 Some other text",
        )


if __name__ == "__main__":
    unittest.main()
