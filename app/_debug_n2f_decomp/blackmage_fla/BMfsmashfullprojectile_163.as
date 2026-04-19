package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class BMfsmashfullprojectile_163 extends MovieClip {
        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;
        public function BMfsmashfullprojectile_163() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(9, frame_10);
            addFrameScript(39, frame_40);
            addFrameScript(64, frame_65);
            addFrameScript(75, frame_76);
            addFrameScript(76, frame_77);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var hitBox:MovieClip;
            var self:*;
            this.self = SSF2API.getProjectile(this);
                        if (SSF2API.isReady() && this.self)
                        {
                            this.self.addEventListener(SSF2Event.ATTACK_HIT, this.toContinue);
                            this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toContinue);
                            this.self.addEventListener(SSF2Event.HIT_WALL, this.wallBounce);
                        };
        }
        internal function frame_10():* {
            this.self.playSound("bmbolt");
                        SSF2API.getCamera().shake(5);
        }
        internal function frame_40():* {
            this.self.refreshAttackID();
        }
        internal function frame_65():* {
            this.self.stancePlayFrame("loop");
        }
        internal function frame_76():* {
            if (this.self == null)
                        {
                            this.self = SSF2API.getProjectile(this);
                        };
                        this.self.stancePlayFrame("suspend");
        }
        internal function frame_77():* {
            this.self = SSF2API.getProjectile(this);
                        if (SSF2API.isReady() && this.self)
                        {
                            this.self.addEventListener(SSF2Event.ATTACK_HIT, this.toContinue);
                            this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toContinue);
                            this.self.addEventListener(SSF2Event.HIT_WALL, this.wallBounce);
                            this.self.stancePlayFrame("loop");
                        };
        }
    }
}
