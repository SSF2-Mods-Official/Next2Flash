package
{
    import flash.display.MovieClip;

    public dynamic class CrossAfterimage extends MovieClip
    {

        public function CrossAfterimage()
        {
            super();
            addFrameScript(15, this.frame16);
        }

        internal function frame16():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

