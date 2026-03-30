package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class G_WKirby_237 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var gawPalette:Object;
        public var next:Boolean;
        public var release:Boolean;
        public var currentJab:Number;

        public function G_WKirby_237()
        {
            super();
            addFrameScript(0, this.frame1, 9, this.frame10, 16, this.frame17, 19, this.frame20, 24, this.frame25, 30, this.frame31, 34, this.frame35, 39, this.frame40, 45, this.frame46, 49, this.frame50, 54, this.frame55, 63, this.frame64, 66, this.frame67, 73, this.frame74, 84, this.frame85);
        }

        public function checkJab():*
        {
            if (this.next)
            {
                this.self.destroyTimer(this.checkJab);
                this.currentJab++;
                this.release = false;
                this.next = false;
                gotoAndStop(("combo" + this.currentJab.toString()));
                this.self.updateAttackStats({"allowFullInterrupt":false});
            };
        }

        public function loopJab():*
        {
            if (this.next)
            {
                this.self.destroyTimer(this.loopJab);
                this.release = false;
                this.next = false;
                gotoAndStop("loop");
            };
        }

        public function checkButtons():*
        {
            if (!this.self.getControls().BUTTON1)
            {
                this.release = true;
            };
            if (this.release && this.self.getControls().BUTTON1)
            {
                this.next = true;
                this.release = false;
            };
        }

        public function chef():void
        {
            this.self.refreshAttackID();
            this.self.attachEffect("global_dust_heavy");
            this.self.fireProjectile("bacon", 20, -15);
            var _local_1:* = this.self.getCurrentProjectile();
            var _local_2:* = _local_1.getMC();
            _local_1.setPaletteSwapData(this.gawPalette);
            var _local_3:* = SSF2API.randomInteger(45, 80);
            _local_3 = ((this.self.isFacingRight()) ? _local_3 : (180 - _local_3));
            var _local_4:* = 12;
            _local_1.angleControl(_local_4, _local_3);
            var _local_5:Number = SSF2API.random();
            var _local_6:Number = this.self.getGlobalVariable("audio");
            if ((_local_5 > 0.2) && (_local_5 <= 0.4) && (_local_6 != 1))
            {
                this.self.playSound("snd_se_GW_Wave02_Lo");
                this.self.setGlobalVariable("audio", 1);
            }
            else if ((_local_5 > 0.4) && (_local_5 <= 0.6) && (_local_6 != 2))
            {
                this.self.playSound("snd_se_GW_Wave03_Lo");
                this.self.setGlobalVariable("audio", 2);
            }
            else if ((_local_5 > 0.6) && (_local_5 <= 0.8) && (_local_6 != 3))
            {
                this.self.playSound("snd_se_GW_Wave04_Lo");
                this.self.setGlobalVariable("audio", 3);
            }
            else
            {
                this.self.playSound("snd_se_GW_Wave06_Lo");
                this.self.setGlobalVariable("audio", 4);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.gawPalette = {
                "paletteSwap":{
                    "colors":[4294967295, 4289045925, 4283519313, 4284703587, 4280690214],
                    "replacements":[4278190080, 4278190080, 4278190080, 4289572269, 4289572269]
                },
                "paletteSwapPA":{
                    "colors":[4294967295, 4290756543, 4286545791, 4282335039, 4283716692, 4280690214],
                    "replacements":[4278190080, 4278190080, 4278190080, 4278190080, 4283848278, 4289572269]
                }
            };
            if (SSF2API.isReady() && this.self)
            {
                this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.self.toLand);
                this.next = false;
                this.release = false;
                this.currentJab = 1;
                this.self.createTimer(1, -1, this.checkButtons);
            };
        }

        internal function frame10():*
        {
            this.chef();
        }

        internal function frame17():*
        {
            this.self.createTimer(1, -1, this.checkJab);
        }

        internal function frame20():*
        {
            if (!this.next)
            {
                this.self.endAttack();
            };
        }

        internal function frame25():*
        {
            this.chef();
        }

        internal function frame31():*
        {
            this.self.createTimer(1, -1, this.checkJab);
        }

        internal function frame35():*
        {
            if (!this.next)
            {
                this.self.endAttack();
            };
        }

        internal function frame40():*
        {
            this.chef();
        }

        internal function frame46():*
        {
            this.self.createTimer(1, -1, this.checkJab);
        }

        internal function frame50():*
        {
            if (!this.next)
            {
                this.self.endAttack();
            };
        }

        internal function frame55():*
        {
            this.chef();
        }

        internal function frame64():*
        {
            this.self.createTimer(1, -1, this.checkJab);
        }

        internal function frame67():*
        {
            if (!this.next)
            {
                this.self.endAttack();
            };
        }

        internal function frame74():*
        {
            this.chef();
        }

        internal function frame85():*
        {
            this.self.endAttack();
        }


    }
}

