// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//SSF2Asset

package 
{
    import flash.display.MovieClip;
    import flash.system.Security;
    import flash.net.LocalConnection;
    import flash.text.TextFormat;
    import flash.text.TextField;

    public dynamic class SSF2Asset extends MovieClip 
    {

        public static var instance:SSF2Asset;

        private var _register:Object;

        public function SSF2Asset()
        {
            try
            {
                Security.allowDomain("mcleodgaming.com");
            }
            catch(e)
            {
            };
            try
            {
                Security.allowDomain("www.mcleodgaming.com");
            }
            catch(e)
            {
            };
            try
            {
                Security.allowDomain("cdn.mcleodgaming.com");
            }
            catch(e)
            {
            };
            try
            {
                Security.allowDomain("files.mcleodgaming.com");
            }
            catch(e)
            {
            };
            try
            {
                Security.allowDomain("supersmashflash.com");
            }
            catch(e)
            {
            };
            try
            {
                Security.allowDomain("www.supersmashflash.com");
            }
            catch(e)
            {
            };
            try
            {
                Security.allowDomain("files.supersmashflash.com");
            }
            catch(e)
            {
            };
            try
            {
                Security.allowDomain("cdn.supersmashflash.com");
            }
            catch(e)
            {
            };
            try
            {
                Security.allowDomain("ssf2.com");
            }
            catch(e)
            {
            };
            try
            {
                Security.allowDomain("www.ssf2.com");
            }
            catch(e)
            {
            };
            try
            {
                Security.allowDomain("files.ssf2.com");
            }
            catch(e)
            {
            };
            try
            {
                Security.allowDomain("cdn.ssf2.com");
            }
            catch(e)
            {
            };
            this.visible = false;
            stop();
            _register = {};
            SSF2Asset.instance = this;
        }

        public function register(_arg_1:String, _arg_2:*):void
        {
            _register[_arg_1] = _arg_2;
        }

        public function getProp(_arg_1:String):*
        {
            return ((_register[_arg_1]) || (null));
        }

        public function initAPI(_arg_1:*):Class
        {
            var src = _arg_1;
            var result:Class = SSF2API.init(src);
            var localDomainLC:LocalConnection = new LocalConnection();
            var myDomainName:String = localDomainLC.domain;
            if (!((((((myDomainName == "localhost") || (myDomainName == "127.0.0.1")) || (myDomainName.match(/^app#com\.mcleodgaming\.ssf2(?:2|3|4)?$/))) || (myDomainName.match(/mcleodgaming\.com$/))) || (myDomainName.match(/supersmashflash\.com$/))) || (myDomainName.match(/ssf2\.com$/))))
            {
                if (loaderInfo.loader)
                {
                    var menu:* = SSF2API.createCustomMenu(SSF2CustomMenu);
                    menu.show();
                    var mc:MovieClip = menu.getMC();
                    mc.stage.addEventListener("added", function (_arg_1:*=null):void
                    {
                        mc.parent.setChildIndex(mc, (mc.parent.numChildren - 1));
                    });
                    mc.graphics.beginFill(0, 1);
                    mc.graphics.drawRect(0, 0, 640, 360);
                    mc.graphics.endFill();
                    var format:TextFormat = new TextFormat();
                    format.color = 0xFFFFFF;
                    format.size = 16;
                    format.bold = true;
                    format.align = "center";
                    format.font = "Verdana";
                    var message:TextField = new TextField();
                    message.defaultTextFormat = format;
                    message.multiline = true;
                    message.x = 10;
                    message.y = 10;
                    message.width = 620;
                    message.height = 340;
                    message.wordWrap = true;
                    message.htmlText = ["Woah there!", "", "Looks like you're trying to play SSF2 on an unofficial website... We don't allow this for your security - the game isn't done and we want to make sure you're playing the latest and greatest update, untampered!", "", "Please ask the administrator of this website to remove the game from their servers, and notify us at devs@supersmashflash.com  right away.", "", "To play this game, please go to", "", "", '<font color="#bfd5ff"><a href="https://www.supersmashflash.com">https://www.supersmashflash.com</a></font>'].join("<br>");
                    mc.addChild(message);
                };
            };
            return (result);
        }

        public function deinitAPI():void
        {
            SSF2API.deinit();
        }


    }
}//package 

