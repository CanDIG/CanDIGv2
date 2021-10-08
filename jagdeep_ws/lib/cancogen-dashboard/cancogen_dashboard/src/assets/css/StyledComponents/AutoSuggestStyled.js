import styled from 'styled-components';

const AutoSuggestStyle = styled.div`
    div.react-autosuggest__container {
        // display: inline-block;
        // padding: 10px 15px;
        font-size: 14px;
        border-radius: 0;
        -webkit-appearance: none;
    }

    .react-autosuggest__suggestions-container {
        display: none;
      }
      
      .react-autosuggest__suggestions-container--open {
        display: block;
        position: absolute;
        top: 51px;
        width: 280px;
        border: 1px solid #aaa;
        background-color: #fff;
        font-family: Helvetica, sans-serif;
        font-weight: 300;
        font-size: 16px;
        border-bottom-left-radius: 4px;
        border-bottom-right-radius: 4px;
        z-index: 10;
      }
      
      .react-autosuggest__suggestions-list {
        margin: 0;
        padding: 0;
        list-style-type: none;
      }
      
      .react-autosuggest__suggestion {
        cursor: pointer;
        padding: 10px 20px;
      }
      
      .react-autosuggest__suggestion--highlighted {
        background-color: #ddd;
      }
      


`;

export default AutoSuggestStyle;
