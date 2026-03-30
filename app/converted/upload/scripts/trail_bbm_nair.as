package
{
    import flash.display.MovieClip;

    public dynamic class trail_bbm_nair extends MovieClip
    {

        public function trail_bbm_nair()
        {
            super();
            addFrameScript(4, this.frame5);
        }

        internal function frame5():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

