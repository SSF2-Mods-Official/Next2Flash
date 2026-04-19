package blackmage_fla {
    import flash.display.BlendMode;
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class UThrow2_Demi_76 extends MovieClip {
        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:BlackMageExt;
        public var xframe:String;
        public var basedamage:*;
        public var effect1:*;
        public var effect2:*;
        public var opp:*;
        public var damage:*;
        public var pow:*;
        public var fullcalc:*;
        public var calcdiv:*;
        public var curcalc:*;
        public var rounded:*;
        public function UThrow2_Demi_76() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(2, frame_3);
            addFrameScript(3, frame_4);
            addFrameScript(10, frame_11);
            addFrameScript(12, frame_13);
            addFrameScript(13, frame_14);
            addFrameScript(14, frame_15);
            addFrameScript(15, frame_16);
            addFrameScript(16, frame_17);
            addFrameScript(20, frame_21);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var touchBox:MovieClip;
            var self:BlackMageExt;
            var xframe:String;
            var basedamage:*;
            var effect1:*;
            var effect2:*;
            var opp:*;
            var damage:*;
            var pow:*;
            var fullcalc:*;
            var calcdiv:*;
            var curcalc:*;
            var rounded:*;
            if (SSF2API.isReady())
                        {
                            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        };
                        this.xframe = null;
                        this.basedamage = 17;
        }
        internal function frame_3():* {
            this.self.playSound("grab_swing4");
        }
        internal function frame_4():* {
            this.self.playSound("blackmage_demi");
                        this.self.swapDepthsWithGrabbedOpponent(false);
                        this.effect1 = this.self.attachEffect("blackmage_demieffect", {
                            "syncHitStun":true,
                            "behind":true
                        });
                        this.effect2 = this.self.getGrabbedOpponent().attachEffect("blackmage_demieffect", {
                            "absolute":true,
                            "x":this.self.getX(),
                            "y":this.self.getY(),
                            "syncHitStun":true
                        });
                        this.effect2.scaleX = this.effect1.scaleX;
                        SSF2API.print(this.effect1.scaleX.toString());
                        SSF2API.print(this.effect2.scaleX.toString());
                        SSF2API.print(this.effect1.x.toString());
                        SSF2API.print(this.effect2.x.toString());
                        this.effect2.blendMode = BlendMode.SCREEN;
                        this.effect2.alpha = 0.5;
        }
        internal function frame_11():* {
            this.xframe = "attack";
        }
        internal function frame_13():* {
            this.opp = this.self.getGrabbedOpponent();
                        this.damage = this.opp.getDamage();
                        this.basedamage /= 3;
                        this.pow = 12.82;
                        this.fullcalc = Math.pow(this.basedamage, this.pow);
                        this.calcdiv = (this.fullcalc / this.basedamage);
                        this.curcalc = Math.pow((this.basedamage * ((999 - this.damage) / 999)), this.pow);
                        this.rounded = (Math.floor(((this.curcalc / this.calcdiv) * 1000)) / 1000);
                        this.self.updateAttackBoxStats(1, {"damage":this.rounded});
                        this.self.playSound("brawl_kick_m");
                        SSF2API.getCamera().shake(5);
        }
        internal function frame_14():* {
            this.self.getGrabbedOpponent().attachEffect("ground_bounce");
        }
        internal function frame_15():* {
            this.self.refreshAttackID();
        }
        internal function frame_16():* {
            this.self.refreshAttackID();
        }
        internal function frame_17():* {
            this.self.updateAttackBoxStats(1, {
                            "damage":1,
                            "power":50,
                            "direction":95,
                            "hasEffect":true,
                            "kbConstant":170,
                            "effectSound":"brawl_kick_l"
                        });
                        this.self.refreshAttackID();
                        SSF2API.getCamera().shake(8);
        }
        internal function frame_21():* {
            this.self.endAttack();
        }
    }
}
