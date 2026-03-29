package battlefield_fla
{
    import flash.display.MovieClip;

    public dynamic class warningbounds_ur_22 extends MovieClip
    {

        public var type:String;

        public function warningbounds_ur_22()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.type = "r_bound_upper";
            this.visible = false;
        }


    }
}

