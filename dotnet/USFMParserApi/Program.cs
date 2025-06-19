using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using System;
using System.Collections.Generic;
using System.IO;
using USFMToolsSharp;
using USFMToolsSharp.Renderers.HTML;
using USFMToolsSharp.Models.Markers;

namespace USFMParserApi
{
    public class Program
    {
        public static void Main(string[] args)
        {
            CreateHostBuilder(args).Build().Run();
        }

        public static IHostBuilder CreateHostBuilder(string[] args) =>
            Host.CreateDefaultBuilder(args)
                .ConfigureWebHostDefaults(webBuilder =>
                {
                    webBuilder.UseStartup<Startup>();
                    webBuilder.UseUrls("http://*:80");
                });
    }

    public class Startup
    {
        public void ConfigureServices(IServiceCollection services)
        {
            services.AddControllers();
        }

        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            app.UseRouting();
            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllers();
            });
        }
    }

    [Route("api/[controller]")]
    [ApiController]
    public class ConverterController : ControllerBase
    {
        [HttpPost("convert")]
        public IActionResult Convert([FromBody] ConversionRequest request)
        {
            if (request == null || string.IsNullOrWhiteSpace(request.InputFile) || string.IsNullOrWhiteSpace(request.OutputFile))
            {
                return BadRequest("Invalid request.");
            }

            if (!System.IO.File.Exists(request.InputFile))
            {
                return NotFound("Input file does not exist.");
            }

            try
            {
                string contents = System.IO.File.ReadAllText(request.InputFile);
                USFMParser parser = new USFMParser();
                USFMDocument document = parser.ParseFromString(contents);
                HTMLConfig configHTML = new HTMLConfig(new List<string>(), partialHTML: true);
                HtmlRenderer renderer = new HtmlRenderer(configHTML);
                string html = renderer.Render(document);
                System.IO.File.WriteAllText(request.OutputFile, html);
                return Ok(true); // Indicating success
            }
            catch
            {
                return StatusCode(500, "An error occurred during processing.");
            }
        }
    }

    [Route("health")]
    [ApiController]
    public class HealthController : ControllerBase
    {
        [HttpGet("status")]
        public IActionResult GetHealthStatus()
        {
            return Ok(new { status = "Healthy" }); // You can customize this response as needed
        }
    }

    public class ConversionRequest
    {
        public string? InputFile { get; set; }  // Mark as nullable
        public string? OutputFile { get; set; } // Mark as nullable
    }
}
