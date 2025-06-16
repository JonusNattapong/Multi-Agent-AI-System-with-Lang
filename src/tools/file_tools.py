"""
File operation tools for agents
"""
import os
import json
from typing import Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from datetime import datetime
from src.utils import get_logger

logger = get_logger("tools.files")

class SaveContentInput(BaseModel):
    """Input for save content tool"""
    content: str = Field(description="Content to save")
    filename: str = Field(description="Name of the file")
    file_type: str = Field(default="txt", description="Type of file (txt, md, json, etc.)")

class SaveContentTool(BaseTool):
    """Tool for saving content to files"""
    
    name = "save_content"
    description = "Save content to a file"
    args_schema = SaveContentInput
    
    def _run(self, content: str, filename: str, file_type: str = "txt") -> str:
        """Save content to a file"""
        logger.info(f"Saving content to {filename}.{file_type}")
        
        try:
            # Create outputs directory if it doesn't exist
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)
            
            # Prepare full filename
            if not filename.endswith(f".{file_type}"):
                filename = f"{filename}.{file_type}"
            
            filepath = os.path.join(output_dir, filename)
            
            # Save content
            with open(filepath, 'w', encoding='utf-8') as f:
                if file_type == "json":
                    json.dump({"content": content, "timestamp": datetime.now().isoformat()}, f, indent=2)
                else:
                    f.write(content)
            
            return f"Content successfully saved to {filepath}"
            
        except Exception as e:
            error_msg = f"Error saving file: {str(e)}"
            logger.error(error_msg)
            return error_msg

class LoadContentInput(BaseModel):
    """Input for load content tool"""
    filename: str = Field(description="Name of the file to load")

class LoadContentTool(BaseTool):
    """Tool for loading content from files"""
    
    name = "load_content"
    description = "Load content from a file"
    args_schema = LoadContentInput
    
    def _run(self, filename: str) -> str:
        """Load content from a file"""
        logger.info(f"Loading content from {filename}")
        
        try:
            # Try different possible locations
            possible_paths = [
                filename,
                os.path.join("outputs", filename),
                os.path.join("data", filename),
            ]
            
            for filepath in possible_paths:
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        if filepath.endswith('.json'):
                            data = json.load(f)
                            return data.get('content', str(data))
                        else:
                            return f.read()
            
            return f"File not found: {filename}"
            
        except Exception as e:
            error_msg = f"Error loading file: {str(e)}"
            logger.error(error_msg)
            return error_msg

class ListFilesInput(BaseModel):
    """Input for list files tool"""
    directory: str = Field(default="outputs", description="Directory to list files from")
    file_type: Optional[str] = Field(default=None, description="Filter by file type")

class ListFilesTool(BaseTool):
    """Tool for listing files in a directory"""
    
    name = "list_files"
    description = "List files in a directory"
    args_schema = ListFilesInput
    
    def _run(self, directory: str = "outputs", file_type: Optional[str] = None) -> str:
        """List files in a directory"""
        logger.info(f"Listing files in {directory}")
        
        try:
            if not os.path.exists(directory):
                return f"Directory not found: {directory}"
            
            files = os.listdir(directory)
            
            # Filter by file type if specified
            if file_type:
                files = [f for f in files if f.endswith(f".{file_type}")]
            
            if not files:
                return f"No files found in {directory}" + (f" with type {file_type}" if file_type else "")
            
            # Format file list with details
            file_list = []
            for file in sorted(files):
                filepath = os.path.join(directory, file)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    size = stat.st_size
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    file_list.append(f"{file} ({size} bytes, modified: {modified})")
            
            return f"Files in {directory}:\n" + "\n".join(file_list)
            
        except Exception as e:
            error_msg = f"Error listing files: {str(e)}"
            logger.error(error_msg)
            return error_msg

class CreateReportInput(BaseModel):
    """Input for create report tool"""
    title: str = Field(description="Report title")
    sections: Dict[str, str] = Field(description="Report sections with content")
    format_type: str = Field(default="markdown", description="Report format (markdown, txt, json)")

class CreateReportTool(BaseTool):
    """Tool for creating formatted reports"""
    
    name = "create_report"
    description = "Create a formatted report from sections"
    args_schema = CreateReportInput
    
    def _run(self, title: str, sections: Dict[str, str], format_type: str = "markdown") -> str:
        """Create a formatted report"""
        logger.info(f"Creating {format_type} report: {title}")
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if format_type == "markdown":
                report = f"# {title}\n\n"
                report += f"*Generated on {timestamp}*\n\n"
                
                for section_title, content in sections.items():
                    report += f"## {section_title}\n\n{content}\n\n"
                
            elif format_type == "json":
                report = json.dumps({
                    "title": title,
                    "timestamp": timestamp,
                    "sections": sections
                }, indent=2)
                
            else:  # txt format
                report = f"{title}\n{'=' * len(title)}\n\n"
                report += f"Generated on {timestamp}\n\n"
                
                for section_title, content in sections.items():
                    report += f"{section_title}\n{'-' * len(section_title)}\n{content}\n\n"
            
            # Save the report
            filename = f"report_{title.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            save_tool = SaveContentTool()
            save_result = save_tool._run(report, filename, format_type)
            
            return f"Report created successfully.\n{save_result}"
            
        except Exception as e:
            error_msg = f"Error creating report: {str(e)}"
            logger.error(error_msg)
            return error_msg

# Tool registry
FILE_TOOLS = [
    SaveContentTool(),
    LoadContentTool(),
    ListFilesTool(),
    CreateReportTool()
]
