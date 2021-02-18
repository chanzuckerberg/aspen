/// <reference types="node" />
/// <reference types="react" />
/// <reference types="react-dom" />

type HostGenome = {
    id: number;
    name: string;
    samplesCount: number;
    erccOnly: boolean;
};

type Project = {
    id: number;
    name: string;
};

type Sample = {
    id: number;
    privateId: string;
    publicId: string;
    uploadDate: string;
    collectionDate: string;
    collectionLocation: string;
    gisaid?: string;
};

type Tree = {
    id: number;
    name: string;
};
