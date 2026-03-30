package
{
    import flash.display.MovieClip;

    public dynamic class trail_bbm_dash extends MovieClip
    {

        public function trail_bbm_dash()
        {
            super();
            addFrameScript(6, this.frame7);
        }

        internal function frame7():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

