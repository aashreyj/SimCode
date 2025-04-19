import React from 'react';
import Avatar from 'react-avatar';

const Client = ({username,color}) => {
    console.log("CLI:",username,color);
    return (
        <div className="client" >
            <Avatar name={username} size={50} round="14px" color={color} />
            <span className="userName">{username}</span>
        </div>
    );
};

export default Client;