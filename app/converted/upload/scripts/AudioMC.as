package
{
    import flash.display.MovieClip;

    public dynamic class AudioMC extends MovieClip
    {

        public function AudioMC()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            stop();
        }


    }
}

