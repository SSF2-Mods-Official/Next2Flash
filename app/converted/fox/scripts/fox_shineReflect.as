package
{
    import flash.display.MovieClip;

    public dynamic class fox_shineReflect extends MovieClip
    {

        public function fox_shineReflect()
        {
            super();
            addFrameScript(5, this.frame6);
        }

        internal function frame6():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

