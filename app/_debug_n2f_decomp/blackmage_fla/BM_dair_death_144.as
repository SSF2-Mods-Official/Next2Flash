package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class BM_dair_death_144 extends MovieClip {
        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;
        public var loopCount:*;
        public var opponent:*;
        public var character:BlackMageExt;
        public function BM_dair_death_144() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(1, frame_2);
            addFrameScript(3, frame_4);
            addFrameScript(4, frame_5);
            addFrameScript(83, frame_84);
            addFrameScript(88, frame_89);
            addFrameScript(89, frame_90);
            addFrameScript(97, frame_98);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var hitBox:MovieClip;
            var self:*;
            var loopCount:*;
            var opponent:*;
            var character:BlackMageExt;
            this.self = SSF2API.getProjectile(this);
                        this.loopCount = null;
                        this.opponent = null;
                        if (SSF2API.isReady() && this.self)
                        {
                            this.character = (this.self.getOwner() as BlackMageExt);
                            this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.toContinue);
                        };
        }
        internal function frame_2():* {
            this.self.destroy();
        }
        internal function frame_4():* {
            this.self.createTimer(1, 86, this.latch);
                        this.self.playSound("bm_Death_start");
        }
        internal function frame_5():* {
            this.loopCount++;
        }
        internal function frame_84():* {
            SSF2API.getCamera().lightFlash();
        }
        internal function frame_89():* {
            this.self.playSound("bm_Death_finish");
                        this.self.updateAttackBoxStats(1, {
                            "hasEffect":true,
                            "damage":6,
                            "priority":7,
                            "hitStun":-1,
                            "selfHitStun":0,
                            "camShake":20,
                            "direction":270,
                            "power":80,
                            "kbConstant":60,
                            "effectSound":"sw_scratch"
                        });
        }
        internal function frame_90():* {
            this.self.updateProjectileStats({"latch":false});
        }
        internal function frame_98():* {
            this.self.destroy();
        }
    }
}
