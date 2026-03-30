package
{
    import flash.display.MovieClip;

    public dynamic class bomberman_fuse extends MovieClip
    {

        public function bomberman_fuse()
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

