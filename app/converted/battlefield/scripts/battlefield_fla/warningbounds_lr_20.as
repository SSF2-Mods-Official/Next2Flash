package battlefield_fla
{
    import flash.display.MovieClip;

    public dynamic class warningbounds_lr_20 extends MovieClip
    {

        public var type:String;

        public function warningbounds_lr_20()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.type = "r_bound_lower";
            this.visible = false;
        }


    }
}

