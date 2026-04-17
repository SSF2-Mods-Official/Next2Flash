package
{
    import flash.display.MovieClip;

    public dynamic class landmaster_wireframe_mc extends MovieClip
    {

        public function landmaster_wireframe_mc()
        {
            super();
            addFrameScript(40, this.frame41);
        }

        internal function frame41():*
        {
            if (parent != null)
            {
                parent.removeChild(this);
            };
        }


    }
}

