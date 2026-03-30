package
{
    import flash.display.MovieClip;

    public dynamic class trail_bbm_jab extends MovieClip
    {

        public function trail_bbm_jab()
        {
            super();
            addFrameScript(7, this.frame8);
        }

        internal function frame8():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

