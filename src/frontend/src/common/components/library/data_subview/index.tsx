import { escapeRegExp } from "lodash/fp";
import React, { FunctionComponent, useReducer } from "react";
import { Input } from "semantic-ui-react";
import { DataTable } from "src/common/components";
import style from "./index.module.scss";

interface Props {
  data?: TableItem[];
  headers: Header[];
  isLoading: boolean;
  renderer?: CustomRenderer;
}

interface InputOnChangeData {
  [key: string]: string;
  value: string;
}

interface SearchState {
  searching?: boolean;
  results?: TableItem[];
}

function searchReducer(state: SearchState, action: SearchState): SearchState {
  return { ...state, ...action };
}

const DataSubview: FunctionComponent<Props> = ({
  data,
  headers,
  isLoading,
  renderer,
}: Props) => {
  // we are modifying state using hooks, so we need a reducer
  const [state, dispatch] = useReducer(searchReducer, {
    results: data,
    searching: false,
  });

  // search functions
  const searcher = (
    _event: React.ChangeEvent<HTMLInputElement>,
    fieldInput: InputOnChangeData
  ) => {
    const query = fieldInput.value;
    if (data === undefined) {
      return;
    } else if (query.length === 0) {
      dispatch({ results: data });
      return;
    }

    dispatch({ searching: true });

    const regex = new RegExp(escapeRegExp(query), "i");
    const filteredData = data.filter((item) =>
      Object.values(item).some((value) => regex.test(`${value}`))
    );

    dispatch({ results: filteredData, searching: false });
  };

  const render = (tableData: TableItem[]) => {
    return (
      <div className={style.samplesRoot}>
        <div className={style.searchBar}>
          <Input
            icon="search"
            placeholder="Search"
            loading={state.searching}
            onChange={searcher}
          />
        </div>
        <div className={style.samplesTable}>
          <DataTable
            isLoading={isLoading}
            data={tableData}
            headers={headers}
            renderer={renderer}
          />
        </div>
      </div>
    );
  };

  if (state.results === undefined) {
    let tableData: TableItem[] = [];
    if (data !== undefined) {
      dispatch({ results: data });
      tableData = data;
    }
    return render(tableData);
  }

  return render(state.results);
};

export { DataSubview };
