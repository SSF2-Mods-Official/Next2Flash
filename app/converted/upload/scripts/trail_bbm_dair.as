package
{
    import flash.display.MovieClip;

    public dynamic class trail_bbm_dair extends MovieClip
    {

        public function trail_bbm_dair()
        {
            super();
            addFrameScript(7, this.frame8);
        }

        internal function frame8():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

