package
{
    import flash.display.MovieClip;

    public dynamic class fox_shineStart extends MovieClip
    {

        public function fox_shineStart()
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

