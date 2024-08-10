using System;
using System.IO;
using System.Collections.Generic;
using USFMToolsSharp;
using USFMToolsSharp.Renderers.HTML;
using USFMToolsSharp.Models.Markers;

namespace USFMParserDriver
{
    class Program
    {
        static void Main(string[] args)
        {

                if (args.Length < 2)
                {
                    Console.WriteLine("Please provide both the input file name and the output file path as command line arguments.");
                    return;
                }

                string inputFile = args[0];
                string outputFile = args[1];

                if (!File.Exists(inputFile))
                {
                    Console.WriteLine("Input file does not exist.");
                    return;
                }

                try
                {
                    string contents = File.ReadAllText(inputFile);
                    USFMToolsSharp.USFMParser parser = new USFMParser();
                    USFMDocument document = parser.ParseFromString(contents);
                    // Console.WriteLine("contents");
                    // Console.WriteLine(contents);
                    HTMLConfig configHTML = new HTMLConfig(new List<string>(), partialHTML: true);
                    HtmlRenderer renderer = new HtmlRenderer(configHTML);
                    string html = renderer.Render(document);
                    // Console.WriteLine(html);
                    File.WriteAllText(outputFile, html);
                    Console.WriteLine("Conversion completed successfully. Output written to: " + outputFile);
                }
                catch (Exception ex)
                {
                    Console.WriteLine("An error occurred: " + ex.Message);
                }
            }


    }
}
