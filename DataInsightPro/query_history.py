import json
import os
from datetime import datetime
from typing import List, Dict, Any

class QueryHistoryManager:
    """Manages query history for the data analysis tool."""
    
    def __init__(self, history_file: str = "query_history.json"):
        """Initialize query history manager."""
        self.history_file = history_file
        self.history = self._load_history()
    
    def add_query(self, question: str, sql_query: str, result_count: int) -> None:
        """Add a new query to the history."""
        query_entry = {
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'sql_query': sql_query,
            'result_count': result_count
        }
        
        self.history.append(query_entry)
        
        # Keep only the last 100 queries to prevent file from growing too large
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        self._save_history()
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get the complete query history."""
        return self.history
    
    def get_recent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent queries."""
        return self.history[-limit:] if len(self.history) >= limit else self.history
    
    def search_history(self, search_term: str) -> List[Dict[str, Any]]:
        """Search through query history."""
        search_term = search_term.lower()
        matching_queries = []
        
        for query in self.history:
            if (search_term in query['question'].lower() or 
                search_term in query['sql_query'].lower()):
                matching_queries.append(query)
        
        return matching_queries
    
    def get_popular_queries(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the most frequently asked similar queries."""
        # Simple implementation - could be enhanced with more sophisticated similarity matching
        query_patterns = {}
        
        for query in self.history:
            # Create a simple pattern based on first few words
            pattern = ' '.join(query['question'].lower().split()[:3])
            if pattern in query_patterns:
                query_patterns[pattern]['count'] += 1
                query_patterns[pattern]['queries'].append(query)
            else:
                query_patterns[pattern] = {
                    'count': 1,
                    'queries': [query]
                }
        
        # Sort by count and return most popular
        popular = sorted(query_patterns.items(), key=lambda x: x[1]['count'], reverse=True)
        
        result = []
        for pattern, data in popular[:limit]:
            # Return the most recent query from each pattern
            result.append(data['queries'][-1])
        
        return result
    
    def clear_history(self) -> None:
        """Clear all query history."""
        self.history = []
        self._save_history()
    
    def export_history(self, filename: str = None) -> str:
        """Export query history to a file."""
        if filename is None:
            filename = f"query_history_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.history, f, indent=2)
            return filename
        except Exception as e:
            raise Exception(f"Error exporting history: {str(e)}")
    
    def import_history(self, filename: str) -> None:
        """Import query history from a file."""
        try:
            with open(filename, 'r') as f:
                imported_history = json.load(f)
            
            # Validate the structure
            if isinstance(imported_history, list):
                for query in imported_history:
                    if not all(key in query for key in ['timestamp', 'question', 'sql_query', 'result_count']):
                        raise ValueError("Invalid history file format")
                
                self.history.extend(imported_history)
                self._save_history()
            else:
                raise ValueError("History file must contain a list of queries")
                
        except Exception as e:
            raise Exception(f"Error importing history: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about query history."""
        if not self.history:
            return {
                'total_queries': 0,
                'date_range': None,
                'most_common_words': [],
                'avg_results_per_query': 0
            }
        
        total_queries = len(self.history)
        
        # Date range
        dates = [datetime.fromisoformat(q['timestamp']) for q in self.history]
        date_range = {
            'earliest': min(dates).isoformat(),
            'latest': max(dates).isoformat()
        }
        
        # Most common words in questions
        all_words = []
        total_results = 0
        
        for query in self.history:
            words = query['question'].lower().split()
            all_words.extend([word for word in words if len(word) > 3])  # Filter short words
            total_results += query['result_count']
        
        # Count word frequency
        word_freq = {}
        for word in all_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        most_common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_queries': total_queries,
            'date_range': date_range,
            'most_common_words': most_common_words,
            'avg_results_per_query': total_results / total_queries if total_queries > 0 else 0
        }
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load query history from file."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            # If there's an error loading the file, start with empty history
            return []
    
    def _save_history(self) -> None:
        """Save query history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            # If we can't save the history, at least keep it in memory
            pass
