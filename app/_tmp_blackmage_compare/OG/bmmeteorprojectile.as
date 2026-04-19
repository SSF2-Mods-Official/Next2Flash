package
{
    import flash.display.MovieClip;

    public dynamic class bmmeteorprojectile extends MovieClip
    {

        public var stance:MovieClip;

        public function bmmeteorprojectile()
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

