from typing import Any, Dict, List, Tuple

ErrorResponseType = Tuple[List[str] | List[Any] | Dict[str, Any], int]
SuccessResponseType = Dict[str, Any] | Tuple[Dict[str, Any], int]
TokenDictType = dict[str, object]
