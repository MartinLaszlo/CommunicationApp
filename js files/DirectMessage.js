import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import moment from 'moment';
import { FaTelegramPlane, FaPaperclip, FaTimesCircle } from "react-icons/fa";

const API_BASE_URL = 'http://localhost:5000';

const DirectMessage = () => {
    const [socket, setSocket] = useState(null);
    const [users, setUsers] = useState([]);
    const [selectedUserId, setSelectedUserId] = useState(null);
    const [currentUser, setCurrentUser] = useState(JSON.parse(localStorage.getItem('user')) || {});
    const [messages, setMessages] = useState([]);
    const [message, setMessage] = useState('');
    const [file, setFile] = useState(null);
    const fileInputRef = useRef(null);
    const messagesEndRef = useRef(null);

    // Initialize socket connection
    useEffect(() => {
        if (currentUser.user_ID) {
            const newSocket = io(`${API_BASE_URL}/direct`, {
                query: `user_ID=${currentUser.user_ID}`
            });
            setSocket(newSocket);

            return () => newSocket.close();
        }
    }, [currentUser.user_ID]);

    // Get all users when component mounts
    useEffect(() => {
        axios.get(`${API_BASE_URL}/users`)
            .then(response => {
                setUsers(response.data);
            })
            .catch(error => console.error('Failed to fetch users', error));
    }, []);

    // Setup Socket.IO to listen for incoming messages
    useEffect(() => {
    const addMessage = (newMessage) => {
        // Check if the message should be displayed in the current chat
        if (newMessage.sender_ID === currentUser.user_ID && newMessage.receiver_ID === selectedUserId ||
            newMessage.receiver_ID === currentUser.user_ID && newMessage.sender_ID === selectedUserId) {
            const formattedMessage = {
                ...newMessage,
                timestamp: moment(newMessage.message_timestamp).calendar(),
                message_content: formatMessageContent(newMessage.message_content),
                sender_name: newMessage.sender_name || 'Fetching...'
            };
            setMessages(prevMessages => [...prevMessages, formattedMessage]);
        }
    };

    if (socket) {
        socket.on('receive_private_message', addMessage);
    }

    return () => {
        if (socket) {
            socket.off('receive_private_message', addMessage);
        }
    };
    }, [socket, selectedUserId, currentUser.user_ID]);

    // Auto-scroll to the bottom of the chat when messages update
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    // Get messages for selected user
    useEffect(() => {
        if (selectedUserId && currentUser.user_ID) {
            fetchMessages();
        }
    }, [selectedUserId, currentUser.user_ID]);

    const fetchMessages = async () => {
        const response = await axios.get(`${API_BASE_URL}/private_messages`, {
            params: { user_id: currentUser.user_ID, target_user_id: selectedUserId }
        });
        setMessages(response.data.map(msg => ({
            ...msg,
            timestamp: moment(msg.message_timestamp).calendar(),
            message_content: formatMessageContent(msg.message_content),
            sender_name: msg.sender_name
        })));
    };

    const formatMessageContent = (content) => {
        if (content.startsWith('file:')) {
            const parts = content.split('|');
            const fileURL = parts[1];
            const fileName = parts[2];
            return /\.(jpg|jpeg|png|gif)$/i.test(fileName) ? 
                (<img src={fileURL} alt={fileName} style={{ maxWidth: '200px', maxHeight: '200px', border: '2px solid var(--file-border-color)', borderRadius: '10px' }} />) :
                (<div style={{ color: 'var(--file-border-color)', border: '2px solid var(--file-border-color)', borderRadius: '10px', padding: '10px', margin: '5px 0' }}>
                    <a href={fileURL} download={fileName} style={{ textDecoration: 'none', color: 'inherit' }}>{fileName}</a>
                    <div style={{ fontSize: 'smaller', color: 'var(--color-info-txt)' }}>Click file name to download.</div>
                </div>);
        }
        return content;
    };

    // Send message
    const sendMessage = async () => {
        if (!message.trim() && !file) return;

        const formData = new FormData();
        formData.append('content', message.trim());
        formData.append('sender_user_id', currentUser.user_ID);
        formData.append('receiver_user_id', selectedUserId);

        if (file) {
            formData.append('file', file);
        }

        try {
            const response = await axios.post(`${API_BASE_URL}/send_private_message`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            // Update other client's UI when message is sent
            socket.emit('send_private_message', {
                ...response.data,
                sender_ID: currentUser.user_ID,
                receiver_ID: selectedUserId,
                message_content: response.data.message_content
            });

            setMessage('');
            setFile(null);
        } catch (error) {
            console.error('Sending message failed:', error);
        }
    };

    const handleInputChange = (event) => {
        setMessage(event.target.value);
    };

    const handleFileButtonClick = () => {
        fileInputRef.current.click();
    };

    const handleFileChange = (event) => {
        const newFile = event.target.files[0];
        if (newFile) {
            setFile(newFile);
        }
    };

    const handleSelectUser = (userId) => {
        setSelectedUserId(userId);
        setMessages([]);
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className='grid grid-cols-12 pl-12 gap-7 p-4 h-[calc(100vh)] bg-gradient-to-b from-background to-background-secondary'>
            <div className='col-start-2 col-span-3 m-0 p-4 flex flex-col text-text bg-primary shadow-lg rounded-3xl overflow-hidden'>
                <div className='text-center text-2xl mt-3 font-bold mb-4'>Direct Messages</div>
                <div className='overflow-y-auto border-2 rounded-3xl border-accent text-lg text-txt' style={{ maxHeight: '900px' }}>
                    {users.map((user) => (
                        <div key={user.user_ID} className={`p-2 hover:bg-accent cursor-pointer hover:text-black transition-all duration-200 ease-linear ${selectedUserId === user.user_ID ? 'bg-button-sec text-white' : ''}`}
                            onClick={() => handleSelectUser(user.user_ID)}>
                            {user.name}
                        </div>
                    ))}
                </div>
            </div>
            <div className='col-start-5 col-span-8 m-0 flex flex-col text-white gap-7 mr-6 bg-primary shadow-lg rounded-3xl overflow-hidden py-2 px-3'>
                <div className="messages max-h-[820px] overflow-y-auto overflow-x-hidden border-2 rounded-3xl border-accent pl-3 bg-primary pr-3">
                    {messages.map((msg, index) => (
                        <div key={index} className="message-bubble my-2 py-2 px-3 flex flex-col bg-tertiary hover:bg-white hover:text-black rounded-3xl transition-all duration-200 ease-linear">
                            <div className="message-header mb-1">
                                <strong className="message-sender" style={{
                                    backgroundColor: '#007bff',
                                    color: 'white',
                                    padding: '2px 6px',
                                    borderRadius: '10px',
                                    marginRight: '4px'
                                }}>{msg.sender_name}</strong>
                                <em className="message-timestamp text-lg" style={{ color: 'var(--color-timestamp)' }}>{msg.timestamp}</em>
                            </div>
                            <div className="message-content text-lg break-words text-text">
                                {msg.message_content}
                            </div>
                        </div>
                    ))}
                    <div ref={messagesEndRef} />
                </div>
                <div className="flex mt-6">
                    <textarea
                        value={message}
                        onChange={handleInputChange}
                        onKeyPress={handleKeyPress}
                        className="shadow appearance-none border border-2 border-accent rounded-l-3xl w-full py-3 px-3 bg-tertiary text-input-txt leading-tight focus:outline-none focus:shadow-outline"
                        placeholder="Type a message..."
                        rows={1}
                        style={{ minHeight: '50px', maxHeight: '150px', overflow: 'auto' }}
                    />
                    {file && (
                        <div className="file-preview flex items-center ml-2 bg-gradient-to-r from-blue-600 to-accent px-2 py-1 text-sm text-white">
                            <img src={URL.createObjectURL(file)} style={{ width: '50px', height: '35px', objectFit: 'contain' }} />
                            <span className="ml-2 truncate">{file.name}</span>
                            <FaTimesCircle onClick={() => setFile(null)} className='text-white' size={25} />
                        </div>
                    )}
                    <button
                        onClick={handleFileButtonClick}
                        className="bg-gradient-to-r text-white from-blue-600 to-accent hover:bg-gradient-to-bl text-gray-800 font-bold py-2 px-4 rounded-l-none rounded-r-none ml-1 focus:outline-none focus:shadow-outline text-base transition duration-300 ease-in-out"
                    >
                        <FaPaperclip className='text-white' size={25} />
                    </button>
                    <button
                        onClick={sendMessage}
                        className="bg-gradient-to-r from-blue-600 to-accent hover:bg-gradient-to-bl focus:outline-none text-white font-bold py-2 px-4 rounded-r-3xl ml-1 focus:outline-none focus:shadow-outline text-base transition duration-300 ease-in-out"
                    >
                        <FaTelegramPlane className='mr-2' size={30} />
                    </button>
                    <input
                        ref={fileInputRef}
                        type="file"
                        onChange={handleFileChange}
                        style={{ display: 'none' }}
                    />
                </div>
            </div>
        </div>
    );
};

export default DirectMessage;
