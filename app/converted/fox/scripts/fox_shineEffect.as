package
{
    import flash.display.MovieClip;

    public dynamic class fox_shineEffect extends MovieClip
    {

        public function fox_shineEffect()
        {
            super();
            addFrameScript(13, this.frame14);
        }

        internal function frame14():*
        {
            stop();
            parent.removeChild(this);
        }


    }
}

