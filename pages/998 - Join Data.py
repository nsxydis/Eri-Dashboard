'''
Example of joining two different datasets together.
'''
import streamlit as st
import polars as pl

def main():
    # Read in the first file
    file1 = st.file_uploader("First Dataset")
    if file1:
        df1 = makeDataframe(file1)
    
    # Read in the second file
    file2 = st.file_uploader("Second Dataset")
    if file2:
        df2 = makeDataframe(file2)

    join = None
    if file1 and file2 and isdf(df1) and isdf(df2):
        # Options for joining the dataframes
        options = [None, 'join', 'stack']
        join = st.selectbox('Join Options', options = options)

    if join == 'join':
        # Figure out which columns are in both datasets
        df1Columns = df1.columns
        df2Columns = df2.columns
        options = [col for col in df1Columns if col in df2Columns]
        by = st.multiselect("Join fields (only keeps values that match in both datasets)", options = options)

        # Check if we have options that aren't being joined on
        if len(by) > 0 and len(by) < len(options):
            string = "You have columns with the same name in both datasets! It" +\
                " is recommended to use all matching columns when joining, or " +\
                "removing them from one of the datasets. Joining in the current " +\
                "state will result in renamed columns."
            st.warning(string)
        if 'continue' not in st.session_state:
            st.session_state['continue'] = None
        if st.button('Join') or st.session_state['continue']:
            if df1[by].schema != df2[by].schema and not st.session_state['continue']:
                # Warning message
                st.warning("The datatypes for the selected columns don't match! You may not get the results you expect if you continue.")
                
                # Show the user the datatypes of the columns they're trying to merge
                st.write("# Dataset 1 Schema:")
                st.write(df1[by].schema)
                st.write("# Dataset 2 Schema:")
                st.write(df2[by].schema)

                if not st.button("Continue?", key = 'continue'):
                    return 1
                    

            # If we're modifying the datasets, do so
            if st.session_state['continue']:
                # Shenanigans to get the column types to match
                df1 = pl.concat([df1, df2[by][0]], how = 'diagonal_relaxed')
                df1 = df1[:len(df1) - 1]
                
                # Repeat for df2
                df2 = pl.concat([df2, df1[by][0]], how = 'diagonal_relaxed')
                df2 = df2[:len(df2) - 1]
                
            try:
                # Join the data frames
                df = df1.join(df2, on = by)
                st.write("# View or download your data")
                st.dataframe(df)
            except:
                st.write("There was an error joining your dataframes!")
                raise
    
    elif join == 'stack':
        try:
            df = pl.concat([df1, df2], how = 'diagonal_relaxed')
            st.write("# View or download your data")
            st.dataframe(df)
        except:
            st.write("There was an error stacking your dataframe")
            raise

def makeDataframe(file):
    # Check if we have a csv file
    if file.name.endswith('.csv'):
        try:
            return pl.read_csv(file, infer_schema_length=None)
        except:
            st.write("There was an issue reading your file!")

    # Otherwise assume we have an excel file
    else:
        try:
            return pl.read_excel(file, read_csv_options= {'infer_schema_length' : None})
        except:
            st.write("There was an issue reading your file!")

def isdf(df):
    '''Checks if something is a dataframe'''
    return type(df) == pl.DataFrame

if __name__ == "__main__":
    main()

    # Each page needs this for the session state to persist
    for k, v in st.session_state.items():
        try:
            st.session_state[k] = v
        except:
            pass