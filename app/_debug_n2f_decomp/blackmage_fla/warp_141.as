package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class warp_141 extends MovieClip {
        public var self:*;
        public var xframe:String;
        public var character:*;
        public function warp_141() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(32, frame_33);
            addFrameScript(43, frame_44);
        }
        internal function frame_1():* {
            var self:*;
            var xframe:String;
            var character:*;
            this.self = SSF2API.getProjectile(this);
                        this.xframe = "charging";
                        if (SSF2API.isReady() && this.self)
                        {
                            this.character = this.self.getOwner();
                            this.self.addToCamera();
                            this.character.addEventListener(SSF2Event.CHAR_HURT, this.projDestroy);
                        };
        }
        internal function frame_33():* {
            this.self.stancePlayFrame("charging");
        }
        internal function frame_44():* {
            this.self.destroy();
        }
    }
}
