package
{
    import flash.display.MovieClip;

    public dynamic class audio extends MovieClip
    {

        public function audio()
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

