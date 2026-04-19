package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class bm_fthrownado_157 extends MovieClip {
        public var self:*;
        public var character:*;
        public function bm_fthrownado_157() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(22, frame_23);
        }
        internal function frame_1():* {
            var self:*;
            var character:*;
            this.self = SSF2API.getProjectile(this);
                        if (SSF2API.isReady() && this.self)
                        {
                            this.character = this.self.getOwner();
                            this.character.addEventListener(SSF2Event.CHAR_HURT, this.remove);
                        };
        }
        internal function frame_23():* {
            this.self.destroy();
        }
    }
}
