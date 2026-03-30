package
{
    import flash.display.MovieClip;

    public dynamic class bm_misstext extends MovieClip
    {

        public function bm_misstext()
        {
            super();
            addFrameScript(21, this.frame22);
        }

        internal function frame22():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

