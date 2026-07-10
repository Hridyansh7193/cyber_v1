import json
import csv
import io
from typing import Any, List, Dict
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

console = Console()

class OutputFormatter:
    @staticmethod
    def render(result: Any, format: str = "text") -> None:
        if format == "json":
            OutputFormatter.render_json(result)
        elif format == "csv":
            if isinstance(result, list):
                OutputFormatter.render_csv(result)
            elif hasattr(result, "model_dump"):
                # Wrap in list if single model
                OutputFormatter.render_csv([result])
            else:
                OutputFormatter.render_error("Cannot render CSV for this data type.")
        else:
            OutputFormatter.render_success(str(result))

    @staticmethod
    def render_json(data: Any) -> None:
        if hasattr(data, "model_dump"):
            console.print_json(json.dumps(data.model_dump(), default=str))
        elif hasattr(data, "__dict__"):
            console.print_json(json.dumps(data.__dict__, default=str))
        else:
            console.print_json(json.dumps(data, default=str))

    @staticmethod
    def render_csv(data: List[Any]) -> None:
        if not data:
            console.print("No data available.")
            return
            
        output = io.StringIO()
        if isinstance(data[0], dict):
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        else:
            # Assume list of pydantic models
            first_item = data[0]
            if hasattr(first_item, "model_dump"):
                fieldnames = list(first_item.model_dump().keys())
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                for row in data:
                    if hasattr(row, "model_dump"):
                        writer.writerow({k: str(v) for k, v in row.model_dump().items()})
            else:
                writer = csv.writer(output)
                for row in data:
                    writer.writerow([str(row)])
        
        console.print(output.getvalue())

    @staticmethod
    def render_table(title: str, columns: List[str], rows: List[List[Any]]) -> None:
        table = Table(title=title)
        for col in columns:
            table.add_column(col)
        for row in rows:
            table.add_row(*[str(item) for item in row])
        console.print(table)

    @staticmethod
    def render_tree(title: str, nodes: Dict[str, Any]) -> None:
        tree = Tree(title)
        
        def add_nodes(current_tree: Tree, current_dict: Dict[str, Any]):
            for k, v in current_dict.items():
                if isinstance(v, dict):
                    branch = current_tree.add(str(k))
                    add_nodes(branch, v)
                elif isinstance(v, list):
                    branch = current_tree.add(str(k))
                    for item in v:
                        branch.add(str(item))
                else:
                    current_tree.add(f"{k}: {v}")
                    
        add_nodes(tree, nodes)
        console.print(tree)

    @staticmethod
    def render_success(msg: str) -> None:
        console.print(f"[green]{msg}[/green]")

    @staticmethod
    def render_error(msg: str) -> None:
        console.print(f"[red]Error: {msg}[/red]")

    @staticmethod
    def render_info(msg: str) -> None:
        console.print(f"[cyan]{msg}[/cyan]")

    @staticmethod
    def render_warning(msg: str) -> None:
        console.print(f"[yellow]Warning: {msg}[/yellow]")

