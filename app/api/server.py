import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from app.services.repair_service import RepairService


class RepoPatcherRequestHandler(BaseHTTPRequestHandler):
    """HTTP API handler for RepoPatcher."""

    def _send_json(self, status_code: int, data: dict):
        response = json.dumps(data).encode("utf-8")

        self.send_response(status_code)
        self.send_header(
            "Content-Type",
            "application/json",
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*",
        )

        self.send_header(
            "Content-Length",
            str(len(response)),
        )
        self.end_headers()

        self.wfile.write(response)

    def do_GET(self):
        if self.path == "/api/health":
            self._send_json(
                200,
                {
                    "success": True,
                    "service": "RepoPatcher",
                    "status": "healthy",
                },
            )
            return

        self._send_json(
            404,
            {
                "success": False,
                "error": "Endpoint not found",
            },
        )

    def do_POST(self):
        if self.path != "/api/repair":
            self._send_json(
                404,
                {
                    "success": False,
                    "error": "Endpoint not found",
                },
            )
            return

        try:
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)

            data = json.loads(body.decode("utf-8"))

            repository_path = data.get("repository_path")
            error = data.get("error")

            if not repository_path:
                self._send_json(
                    400,
                    {
                        "success": False,
                        "error": "repository_path is required",
                    },
                )
                return

            repository = Path(repository_path)

            if not repository.exists():
                self._send_json(
                    400,
                    {
                        "success": False,
                        "error": "Repository path does not exist",
                    },
                )
                return

            if not repository.is_dir():
                self._send_json(
                    400,
                    {
                        "success": False,
                        "error": "repository_path must be a directory",
                    },
                )
                return

            service = RepairService()

            result = service.repair(
                repository_path=str(repository),
                user_error=error,
            )

            self._send_json(200, result)

        except json.JSONDecodeError:
            self._send_json(
                400,
                {
                    "success": False,
                    "error": "Invalid JSON request",
                },
            )

        except Exception as exc:
            self._send_json(
                500,
                {
                    "success": False,
                    "error": str(exc),
                },
            )
            
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""

        self.send_response(204)

        self.send_header(
             "Access-Control-Allow-Origin",
             "*",
            )

        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, OPTIONS",
        )

        self.send_header(
             "Access-Control-Allow-Headers",
             "Content-Type",
            )

        self.end_headers()

    def log_message(self, format, *args):
        """Keep server output clean."""
        print(f"[RepoPatcher] {format % args}")


def start_server(
    host: str = "127.0.0.1",
    port: int = 8000,
):
    """Start the RepoPatcher API server."""

    server = HTTPServer(
        (host, port),
        RepoPatcherRequestHandler,
    )

    print(
        f"RepoPatcher API running at "
        f"http://{host}:{port}"
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping RepoPatcher...")
    finally:
        server.server_close()


if __name__ == "__main__":
    start_server()