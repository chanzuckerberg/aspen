import React, { FunctionComponent } from "react";
import { Table } from "semantic-ui-react";

import style from "./index.module.scss";

type Props = {
    samples?: Array<Sample>;
};

const Samples: FunctionComponent<Props> = ({ samples = [] }) => {

    const tableRows = (data: Array<Sample>): Array<JSX.Element> => {
        return data.map(sample => {
            return (
                <Table.Row>
                    <Table.Cell>{sample.privateId}</Table.Cell>
                    <Table.Cell>{sample.publicId}</Table.Cell>
                    <Table.Cell>{sample.uploadDate}</Table.Cell>
                    <Table.Cell>{sample.collectionDate}</Table.Cell>
                    <Table.Cell>{sample.collectionLocation}</Table.Cell>
                    <Table.Cell>{sample.gisaid}</Table.Cell>
                </Table.Row>
            )
        })
    }

    return (
        <div className={style.samplesRoot}>
            <Table basic="very" singleline>
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell><span className={style.header}>Private ID</span></Table.HeaderCell>
                        <Table.HeaderCell><span className={style.header}>Public ID</span></Table.HeaderCell>
                        <Table.HeaderCell><span className={style.header}>Upload Date</span></Table.HeaderCell>
                        <Table.HeaderCell><span className={style.header}>Collection Date</span></Table.HeaderCell>
                        <Table.HeaderCell><span className={style.header}>Collection Location</span></Table.HeaderCell>
                        <Table.HeaderCell><span className={style.header}>GISAID</span></Table.HeaderCell>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {tableRows(samples)}
                </Table.Body>
            </Table>
        </div>
    )
}

export default Samples;
