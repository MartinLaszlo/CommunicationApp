import React, { useState, useEffect, useRef } from 'react';
import io from 'socket.io-client';
import axios from 'axios';
import moment from 'moment';
import { FaTelegramPlane, FaPaperclip, FaTimesCircle } from "react-icons/fa";

const API_BASE_URL = 'http://localhost:5000';
const socket = io(API_BASE_URL);

const Chat = ({ channelId }) => {
    const [currentUser] = useState(JSON.parse(localStorage.getItem('user')) || {});
    const [messages, setMessages] = useState([]);
    const [message, setMessage] = useState('');
    const [file, setFile] = useState(null);
    const fileInputRef = useRef(null);
    const messagesEndRef = useRef(null);
    // Scroll into message view and include information and timestamp on new message
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    useEffect(() => {
        fetchMessages();

        const handleNewMessage = (msg) => {
            if (msg.channel === channelId) {
                fetchUser(msg.student_ID || msg.staff_ID, !!msg.staff_ID).then(username => {
                    const newMessage = {
                        ...msg,
                        username,
                        isStaff: !!msg.staff_ID,
                        message_content: msg.content,
                        timestamp: msg.timestamp
                    };
                    setMessages(prevMessages => [...prevMessages, newMessage]);
                });
            }
        };

        socket.on('receive_message', handleNewMessage);
        return () => {
            socket.off('receive_message', handleNewMessage);
        };
    }, [channelId]);
    // Get messages
    const fetchMessages = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/channels/${channelId}/messages`);
            const fetchedMessages = response.data || [];
            
            const messagesWithUsernames = await Promise.all(fetchedMessages.map(async (msg) => {
                const isStaff = msg.staff_ID !== null;
                const userId = isStaff ? msg.staff_ID : msg.student_ID;
                const username = await fetchUser(userId, isStaff);
                return {
                    ...msg,
                    username,
                    isStaff,
                    timestamp: msg.message_timestamp
                };
            }));

            setMessages(messagesWithUsernames);
        } catch (error) {
            console.error('Error fetching messages:', error);
        }
    };
    // Check if user is staff or student
    const fetchUser = async (userId, isStaff) => {
        const userTypeEndpoint = isStaff ? 'staff' : 'students';
        try {
            const response = await axios.get(`${API_BASE_URL}/${userTypeEndpoint}/${userId}/info`);
            return response.data.username;
        } catch (error) {
            console.error(`Error fetching ${userTypeEndpoint} info:`, error);
            return 'Unknown';
        }
    };
    // Message sending
    const sendMessage = async () => {
        if (message.trim() || file) {
            let content = message.trim();
            if (file) {
                const formData = new FormData();
                formData.append('file', file.file);
                const uploadResponse = await axios.post(`${API_BASE_URL}/uploads`, formData, {
                    headers: {'Content-Type': 'multipart/form-data'}
                });
                content = `file:${uploadResponse.data.filepath}|${file.file.name}`;  
            }
    
            const messageData = {
                content,
                channel: channelId,
                student_ID: currentUser.role === 'student' ? currentUser.id : null,
                staff_ID: currentUser.role === 'staff' ? currentUser.id : null,
                timestamp: new Date().toISOString()
            };
    
            socket.emit('send_message', messageData);
            setMessage('');
            setFile(null);  // Reset file after sending
        }
    };
    
    // Text area resize
    const autoResizeTextArea = () => {
        if (textAreaRef.current) {
            textAreaRef.current.style.height = 'auto';
            textAreaRef.current.style.height = textAreaRef.current.scrollHeight + 'px';
        }
    };

    const handleInputChange = (event) => {
        setMessage(event.target.value);
        autoResizeTextArea();
    };

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (!file) return;
    
        if (file.type.startsWith('image/')) {
            // For image files generate preview
            const reader = new FileReader();
            reader.onload = (e) => {
                setFile({
                    file,
                    preview: e.target.result,
                    name: file.name
                });
            };
            reader.readAsDataURL(file);
        } else {
            // For non-image files keep file name
            setFile({
                file,
                name: file.name
            });
        }
    };
    

    const handleFileButtonClick = () => {
        fileInputRef.current.click();  // Open file selection when paperclip icon is clicked
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            if (event.shiftKey) {
            } else {
                event.preventDefault();
                sendMessage();
            }
        }
    };

    const textAreaRef = useRef(null); // ref for text area to allow for better chatbox scaling

    return (
        <div>
            <div className="messages max-h-[590px] overflow-y-auto overflow-x-hidden border-2 rounded-3xl border-accent pl-3 bg-primary pr-3" >
            {messages.map((msg, index) => {
    let messageContent;
    if (msg.message_content.startsWith('file:')) {
        const parts = msg.message_content.substring(5).split('|');
        const fileURL = parts[0];
        const fileName = parts[1];
        // Check for image file extensions
        if (/\.(jpg|jpeg|png|gif)$/i.test(fileName)) {
            // Image preview
            messageContent = (
                <div>
                    <img src={fileURL} alt={fileName} style={{ maxWidth: '200px', maxHeight: '200px', border: '2px solid var(--file-border-color)', borderRadius: '10px',}} />
                </div>
            );
        } else {
            // Non-image file download link
            messageContent = (
                <div style={{ color: 'var(--file-border-color)', border: '2px solid var(--file-border-color)', borderRadius: '10px', padding: '10px', margin: '5px 0' }}>
                    <a href={fileURL} download={fileName} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none', color: 'var(--file-border-color)' }}>
                        {fileName}
                    </a>
                    <div style={{ fontSize: 'smaller', color: 'var(--color-info-txt)' }}>Click file name to download.</div>
                </div>
            );
        }
    } else if (msg.message_content.startsWith('<img')) {
        // Handle embedded image HTML
        messageContent = <div dangerouslySetInnerHTML={{ __html: msg.message_content }} />;
    } else {
        // Text content
        messageContent = msg.message_content || 'No message content';
    }

    return (
        <div key={index} className="message-bubble my-2 py-2 px-3 flex flex-col bg-tertiary hover:bg-white hover:text-black rounded-3xl transition-all duration-200 ease-linear">
            <div className="message-header mb-1 text-lg">
                <strong style={{
                    backgroundColor: msg.isStaff ? '#dc3545' : '#007bff',
                    color: 'white',
                    padding: '2px 6px',
                    borderRadius: '10px',
                    marginRight: '4px'
                }}>{msg.isStaff ? 'Staff ★' : 'Student'}</strong>
                <span style={{ marginRight: '8px' }}>{msg.username}</span>
                <em style={{ color: 'var(--color-timestamp)' }}>{moment(msg.timestamp).calendar()}</em>
            </div>
            <div className="message-content text-lg break-words">
                {messageContent}
            </div>
        </div>
    );
})}
        <div ref={messagesEndRef} />
            </div>
            <div className="flex mt-6">
                <textarea
                    ref={textAreaRef}
                    value={message}
                    onChange={handleInputChange}
                    onKeyPress={handleKeyPress}
                    className="shadow appearance-none border border-2 border-accent rounded-l-3xl w-full py-3 px-3 bg-tertiary text-input-txt leading-tight focus:outline-none focus:shadow-outline"
                    placeholder="Type a message..."
                    rows={1}
                    style={{ minHeight: '50px', maxHeight: '150px', overflow: 'auto' }}
                />
                {file && (
                        <div className="file-preview flex items-center ml-2 bg-gradient-to-r from-blue-600 to-accent px-2 py-1">
                            {file.preview ? (
                                <img src={file.preview} alt={file.name} style={{ width: '50px', height: '35px', objectFit: 'contain'}} />
                            ) : (
                                <span className="text-sm text-white ml-2">{file.name}</span>
                            )}
                            
                            <button onClick={() => setFile(null)} className="ml-2 text-white"><FaTimesCircle className='text-red' size={25} /></button>
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
    );
    
};

export default Chat;
