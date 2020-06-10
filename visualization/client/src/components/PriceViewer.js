import React, {useState, useEffect} from "react";
import Select from 'react-select';
import axios from 'axios';
import {BASE_URL} from '../urls';
import Chart from "./Chart";

const PriceViewer = () => {
    const [itemData, setItemData] = useState([]);
    const [items, setItems] = useState();
    useEffect(
        () => axios.get(BASE_URL + "items_list")
            .then(resp => setItems(resp.data))
            .catch(err => console.log(err)),
        [],
    );
    return <div>
        <Select
            options={items}
            onChange={(item) => axios.get(BASE_URL + "item/" + item.value)
                .then(response => setItemData(response.data))
                .catch(err => console.log(err))}
        />
        <div style={{"height": 10}}/>
        <Chart
            data={itemData}
        />

    </div>
};

export default PriceViewer;