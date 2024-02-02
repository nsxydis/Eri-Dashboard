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
            st.warning("You have columns with the same name in both datasets! Joining in this state may result in renamed columns.")
        if st.button('Join'):
            try:
                df = df1.join(df2, on = by)
                st.write("# View or download your data")
                st.dataframe(df)
            except:
                st.write("There was an error joining your dataframes!")
                raise
    
    elif join == 'stack':
        try:
            df = pl.concat([df1, df2], how = 'vertical_relaxed')
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