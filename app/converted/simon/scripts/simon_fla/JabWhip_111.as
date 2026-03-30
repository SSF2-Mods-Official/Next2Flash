package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class JabWhip_111 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var self:*;

        public function JabWhip_111()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
        }


    }
}

