package
{
    import flash.display.MovieClip;

    public dynamic class blasterhit extends MovieClip
    {

        public function blasterhit()
        {
            super();
            addFrameScript(4, this.frame5);
        }

        internal function frame5():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

